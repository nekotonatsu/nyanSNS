from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    display_name = Column(
        String(100),
        nullable=True
    )

    bio = Column(
        Text,
        nullable=True
    )

    avatar_url = Column(
        String(500),
        nullable=True
    )

    score = Column(
        Integer,
        default=100,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    is_admin = Column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        onupdate=lambda:datetime.now(timezone.utc)
    )

    posts = relationship(
        "Post",
        back_populates="author",
        cascade="all, delete-orphan"
    )

    comments = relationship(
        "Comment",
        back_populates="author",
        cascade="all, delete-orphan"
    )

    likes = relationship(
        "Like",
        back_populates="user",
        cascade="all,delete-orphan"
    )

    followers = relationship(
        "Follow",
        foreign_keys="Follow.followed_id",
        back_populates="followed"
    )

    following = relationship(
        "Follow",
        foreign_keys="Follow.follower_id",
        back_populates="follower"
    )

    sent_messages = relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender"
    )

    received_messages = relationship(
        "Message",
        foreign_keys="Message.receiver_id",
        back_populates="receiver"
    )

    score_logs = relationship(
        "ScoreLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )