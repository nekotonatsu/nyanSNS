from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_ip, get_current_user
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_otp_secret,
    generate_totp,
    hash_password,
    verify_password,
    verify_totp,
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    OTPSetupRequest,
    OTPVerifyRequest,
    RefreshRequest,
    RegisterRequest,
    TempTokenResponse,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

RATE_LIMIT_REGISTER_IP = 3  # 同一IPから1時間以内の最大登録数


@router.post("/register", response_model=TempTokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    client_ip = get_client_ip(http_request)

    # IP別レート制限
    rate_key = f"register_rate:{client_ip}"
    count = await redis.incr(rate_key)
    if count == 1:
        await redis.expire(rate_key, 3600)
    if count > RATE_LIMIT_REGISTER_IP:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="同一IPからの登録が多すぎます。しばらく後にお試しください。",
        )

    # 重複チェック
    existing = await db.execute(
        select(User).where(
            (User.email == request.email) | (User.username == request.username)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="メールアドレスまたはユーザー名はすでに使用されています",
        )

    otp_secret = generate_otp_secret()
    user = User(
        username=request.username,
        email=request.email,
        display_name=request.display_name,
        hashed_password=hash_password(request.password),
        otp_secret=otp_secret,
        otp_enabled=True,
        otp_verified=False,
        registration_ip=client_ip,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # OTPコードをメール送信（開発環境ではRedisにキャッシュして確認用エンドポイントで取得可能）
    otp_code = generate_totp(otp_secret)
    await redis.setex(f"otp_setup:{user.id}", 300, otp_code)

    temp_token = create_access_token(f"setup:{user.id}")

    return TempTokenResponse(temp_token=temp_token)


@router.post("/register/verify-otp", response_model=TokenResponse)
async def verify_registration_otp(
    body: OTPVerifyRequest,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    try:
        payload = decode_token(body.temp_token)
        sub = payload.get("sub", "")
        if not sub.startswith("setup:"):
            raise ValueError
        user_id = int(sub.split(":")[1])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="無効なトークンです")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")

    if not verify_totp(user.otp_secret, body.otp_code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTPコードが無効です")

    user.otp_verified = True
    await db.commit()

    await redis.delete(f"otp_setup:{user.id}")

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/login")
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="アカウントが無効化されています")

    if user.otp_enabled and user.otp_verified:
        # OTP検証が必要
        otp_code = generate_totp(user.otp_secret)
        await redis.setex(f"otp_login:{user.id}", 300, otp_code)
        temp_token = create_access_token(f"login:{user.id}")
        return TempTokenResponse(temp_token=temp_token)

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/login/verify-otp", response_model=TokenResponse)
async def verify_login_otp(
    body: OTPVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = decode_token(body.temp_token)
        sub = payload.get("sub", "")
        if not sub.startswith("login:"):
            raise ValueError
        user_id = int(sub.split(":")[1])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="無効なトークンです")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")

    if not verify_totp(user.otp_secret, body.otp_code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTPコードが無効です")

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="無効なリフレッシュトークンです")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="ユーザーが見つかりません")

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.get("/otp/setup")
async def get_otp_setup_info(current_user: User = Depends(get_current_user)):
    """OTP設定情報を返す（開発環境確認用も兼ねる）"""
    import pyotp
    totp = pyotp.TOTP(current_user.otp_secret)
    return {
        "otp_uri": totp.provisioning_uri(current_user.email, issuer_name="nyanSNS"),
        "secret": current_user.otp_secret,
    }
