from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class Like(Base):
    __tablename__ = "likes"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "post_id",
            name="uq_user_post_like"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    post_id = Column(
        Integer,
        ForeignKey("posts.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")