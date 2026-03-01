from datetime import UTC, datetime, timedelta

import bcrypt
import pyotp
from jose import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def generate_otp_secret() -> str:
    return pyotp.random_base32()


def generate_totp(secret: str) -> str:
    totp = pyotp.TOTP(secret, interval=settings.OTP_EXPIRE_SECONDS)
    return totp.now()


def verify_totp(secret: str, otp: str) -> bool:
    totp = pyotp.TOTP(secret, interval=settings.OTP_EXPIRE_SECONDS)
    return totp.verify(otp, valid_window=1)
