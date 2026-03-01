from enum import IntEnum

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.score_log import ScoreLog


class ScoreDelta(IntEnum):
    """スコア変動値の定義"""
    # 加算
    POST_CREATED = 5
    LIKE_RECEIVED = 3
    COMMENT_RECEIVED = 2
    FOLLOWED = 4

    # 減算（負の値）
    POST_DELETED = -3
    LIKE_REMOVED = -2
    REPORTED = -20
    SPAM_DETECTED = -50


SCORE_REASON_MAP: dict[str, int] = {
    "post_created": ScoreDelta.POST_CREATED,
    "post_deleted": ScoreDelta.POST_DELETED,
    "like_received": ScoreDelta.LIKE_RECEIVED,
    "like_removed": ScoreDelta.LIKE_REMOVED,
    "comment_received": ScoreDelta.COMMENT_RECEIVED,
    "followed": ScoreDelta.FOLLOWED,
    "reported": ScoreDelta.REPORTED,
    "spam_detected": ScoreDelta.SPAM_DETECTED,
}


async def apply_score(db: AsyncSession, user_id: int, reason: str) -> int:
    """スコアを変動させてスコアログを記録する。変動後のスコアを返す。"""
    delta = SCORE_REASON_MAP.get(reason)
    if delta is None:
        raise ValueError(f"Unknown score reason: {reason}")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()

    new_score = user.score + delta

    await db.execute(update(User).where(User.id == user_id).values(score=new_score))

    log = ScoreLog(user_id=user_id, delta=delta, reason=reason, score_after=new_score)
    db.add(log)
    await db.flush()

    return new_score
