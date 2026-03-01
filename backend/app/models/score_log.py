from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ScoreLog(Base):
    """スコア変動ログ - ユーザーのスコア変動履歴を記録する"""
    __tablename__ = "score_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    delta: Mapped[int] = mapped_column(Integer, nullable=False)  # 正=加算、負=減算
    reason: Mapped[str] = mapped_column(String(100), nullable=False)  # "post_created", "like_received", etc.
    score_after: Mapped[int] = mapped_column(Integer, nullable=False)  # 変動後のスコア

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="score_logs")
