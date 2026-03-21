from datetime import datetime
from pydantic import BaseModel
from app.schemas.user import UserPublicResponse

class PostCreateRequest(BaseModel):
    content: str


class PostUpdateRequest(BaseModel):
    content: str

class PostResponse(BaseModel):
    id: int
    content: str
    media_url: str | None
    media_type: str | None
    created_at: datetime
    updated_at: datetime
    author: UserPublicResponse
    likes_count: int = 0
    comments_count: int = 0
    is_liked: bool = False

    model_config = {"from_attributes": True}