from datetime import datetime
from pydantic import BaseModel
from app.schemas.user import UserPublicResponse

class CommentCreateRequest(BaseModel):
    content: str
    parent_id: int | None = None

class CommentResponse(BaseModel):
    id: int
    content: str
    post_id: int
    parent_id: int | None
    created_at: datetime
    author: UserPublicResponse

    model_config = {"from_attributes": True}