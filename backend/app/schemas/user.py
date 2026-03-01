from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    display_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    display_name: str | None = Field(None, min_length=1, max_length=100)
    bio: str | None = Field(None, max_length=500)


class UserRead(UserBase):
    id: int
    bio: str | None
    avatar_url: str | None
    score: int
    otp_enabled: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserPublic(BaseModel):
    """公開プロフィール（スコアに応じてフィルタリング済み）"""
    id: int
    username: str
    display_name: str
    bio: str | None
    avatar_url: str | None
    is_priority: bool
    created_at: datetime

    model_config = {"from_attributes": True}
