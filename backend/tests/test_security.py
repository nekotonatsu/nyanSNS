"""認証・セキュリティのユニットテスト"""
import pytest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_otp_secret,
    generate_totp,
    verify_totp,
)


def test_hash_and_verify_password():
    """パスワードのハッシュ化と検証が正常に動作すること"""
    plain = "secret_password_123"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)
    assert not verify_password("wrong_password", hashed)


def test_access_token_decode():
    """アクセストークンを正しくデコードできること"""
    token = create_access_token("42")
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "access"


def test_refresh_token_decode():
    """リフレッシュトークンを正しくデコードできること"""
    token = create_refresh_token("42")
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["type"] == "refresh"


def test_otp_secret_generation():
    """OTPシークレットが生成できること"""
    secret = generate_otp_secret()
    assert len(secret) > 0
    assert isinstance(secret, str)


def test_totp_generation_and_verification():
    """TOTPコードの生成と検証が正常に動作すること"""
    secret = generate_otp_secret()
    code = generate_totp(secret)
    assert len(code) == 6
    assert code.isdigit()
    assert verify_totp(secret, code)


def test_totp_invalid_code():
    """不正なTOTPコードが拒否されること"""
    secret = generate_otp_secret()
    assert not verify_totp(secret, "000000")
