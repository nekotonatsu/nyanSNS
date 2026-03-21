from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class ScoreLog(Base):
    __tablename__ = "score_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    delta = Column(Integer, nullable=False)

    reason = Column(String(100), nullable=False)

    score_after = Column(Integer, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc)
    )