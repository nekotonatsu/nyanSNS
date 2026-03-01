from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Score system
    score: Mapped[int] = mapped_column(Integer, default=settings.SCORE_INITIAL, nullable=False)

    # OTP
    otp_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)
    otp_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    otp_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Registration metadata
    registration_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author", lazy="select")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="author", lazy="select")
    likes_given: Mapped[list["Like"]] = relationship("Like", back_populates="user", lazy="select")
    score_logs: Mapped[list["ScoreLog"]] = relationship("ScoreLog", back_populates="user", lazy="select")

    following: Mapped[list["Follow"]] = relationship(
        "Follow", foreign_keys="Follow.follower_id", back_populates="follower", lazy="select"
    )
    followers: Mapped[list["Follow"]] = relationship(
        "Follow", foreign_keys="Follow.followed_id", back_populates="followed", lazy="select"
    )

    sent_messages: Mapped[list["Message"]] = relationship(
        "Message", foreign_keys="Message.sender_id", back_populates="sender", lazy="select"
    )
    received_messages: Mapped[list["Message"]] = relationship(
        "Message", foreign_keys="Message.receiver_id", back_populates="receiver", lazy="select"
    )

    @property
    def is_visible(self) -> bool:
        return self.score >= settings.SCORE_HIDDEN_THRESHOLD

    @property
    def is_priority(self) -> bool:
        return self.score >= settings.SCORE_PRIORITY_THRESHOLD
