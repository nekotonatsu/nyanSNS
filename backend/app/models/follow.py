from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Follow(Base):
    __tablename__ = "follows"

    __table_args__ = (
        UniqueConstraint(
            "follower_id",
            "followed_id",
            name="uq_follower_followed"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    follower_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    followed_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    follower = relationship(
        "User",
        foreign_keys=[follower_id],
        back_populates="following"
    )

    followed = relationship(
        "User",
        foreign_keys=[followed_id],
        back_populates="followers"
    )