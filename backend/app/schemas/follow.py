from datetime import datetime

from pydantic import BaseModel

from app.schemas.user import UserPublic


class FollowRead(BaseModel):
    id: int
    follower: UserPublic
    followed: UserPublic
    created_at: datetime

    model_config = {"from_attributes": True}
