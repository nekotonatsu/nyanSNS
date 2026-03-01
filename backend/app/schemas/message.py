from datetime import datetime

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    receiver_id: int
    content: str = Field(..., min_length=1, max_length=1000)


class MessageRead(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
