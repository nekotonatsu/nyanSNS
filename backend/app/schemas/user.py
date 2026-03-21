from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    display_name: str | None
    bio: str | None
    avatar_url: str | None
    score: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserPublicResponse(BaseModel):
    id: int
    username: str
    display_name: str | None
    bio: str | None
    avatar_url: str | None
    score: int
    followers_count: int = 0
    following_count: int = 0
    is_following: bool = False

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    display_name: str | None = None
    bio: str | None = None