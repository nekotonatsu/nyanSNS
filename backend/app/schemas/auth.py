from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    display_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class OTPVerifyRequest(BaseModel):
    temp_token: str
    otp_code: str = Field(..., min_length=6, max_length=6)


class OTPSetupRequest(BaseModel):
    otp_code: str = Field(..., min_length=6, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TempTokenResponse(BaseModel):
    """OTP検証が必要な場合の一時トークン"""
    temp_token: str
    requires_otp: bool = True


class RefreshRequest(BaseModel):
    refresh_token: str
