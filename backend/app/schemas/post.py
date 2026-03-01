from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.user import UserPublic


class PostBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    content: str | None = Field(None, min_length=1, max_length=500)


class PostRead(PostBase):
    id: int
    author_id: int
    author: UserPublic
    media_url: str | None
    media_type: str | None
    likes_count: int = 0
    comments_count: int = 0
    is_liked: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
