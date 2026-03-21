from datetime import datetime
from pydantic import BaseModel
from app.schemas.user import UserPublicResponse

class MessageCreateRequest(BaseModel):
    content: str

class MessageResponse(BaseModel):
    id: int
    content: str
    is_read: bool
    created_at: datetime
    sender: UserPublicResponse
    receiver: UserPublicResponse

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    user: UserPublicResponse
    last_message: MessageResponse | None
    unread_count: int = 0