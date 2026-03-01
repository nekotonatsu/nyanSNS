from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.user import UserPublic


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=300)
    parent_id: int | None = None


class CommentRead(BaseModel):
    id: int
    post_id: int
    author: UserPublic
    content: str
    parent_id: int | None
    replies: list["CommentRead"] = []
    created_at: datetime

    model_config = {"from_attributes": True}
