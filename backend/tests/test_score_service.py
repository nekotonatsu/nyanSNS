"""スコアサービスのユニットテスト"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.score_service import apply_score, SCORE_REASON_MAP, ScoreDelta


def test_score_reason_map_has_expected_reasons():
    """スコア変動理由が定義されていること"""
    expected_reasons = [
        "post_created",
        "post_deleted",
        "like_received",
        "like_removed",
        "comment_received",
        "followed",
        "reported",
        "spam_detected",
    ]
    for reason in expected_reasons:
        assert reason in SCORE_REASON_MAP


def test_score_deltas_are_positive_for_good_actions():
    """良い行動でスコアが加算されること"""
    assert SCORE_REASON_MAP["post_created"] > 0
    assert SCORE_REASON_MAP["like_received"] > 0
    assert SCORE_REASON_MAP["comment_received"] > 0
    assert SCORE_REASON_MAP["followed"] > 0


def test_score_deltas_are_negative_for_bad_actions():
    """悪い行動でスコアが減算されること"""
    assert SCORE_REASON_MAP["post_deleted"] < 0
    assert SCORE_REASON_MAP["like_removed"] < 0
    assert SCORE_REASON_MAP["reported"] < 0
    assert SCORE_REASON_MAP["spam_detected"] < 0


@pytest.mark.asyncio
async def test_apply_score_raises_for_unknown_reason():
    """未知の理由でValueErrorが発生すること"""
    mock_db = AsyncMock()
    with pytest.raises(ValueError, match="Unknown score reason"):
        await apply_score(mock_db, user_id=1, reason="unknown_reason")


def test_score_initial_value():
    """初期スコア設定値が正の値であること"""
    from app.core.config import settings
    assert settings.SCORE_INITIAL > 0


def test_score_threshold_values():
    """スコア閾値が意図通りに設定されていること"""
    from app.core.config import settings
    assert settings.SCORE_HIDDEN_THRESHOLD <= settings.SCORE_INITIAL
    assert settings.SCORE_PRIORITY_THRESHOLD > settings.SCORE_INITIAL
    assert settings.SCORE_HIDDEN_THRESHOLD < settings.SCORE_PRIORITY_THRESHOLD
