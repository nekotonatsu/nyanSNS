from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    post_id = Column(
        Integer,
        ForeignKey("posts.id"),
        nullable=False
    )

    author_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    parent_id = Column(
        Integer,
        ForeignKey("comments.id"),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc)
    )

    post = relationship(
        "Post",
        back_populates="comments"
    )

    author = relationship(
        "User",
        back_populates="comments"
    )

    replies = relationship(
        "Comment",
        backref="parent",
        remote_side=[id]
    )