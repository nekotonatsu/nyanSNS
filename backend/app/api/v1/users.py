from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.models.follow import Follow
from app.models.user import User
from app.schemas.user import UserPublic, UserRead, UserUpdate
from app.services.score_service import apply_score

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_me(
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.display_name is not None:
        current_user.display_name = body.display_name
    if body.bio is not None:
        current_user.bio = body.bio
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/{username}", response_model=UserPublic)
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user or not user.is_visible:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")

    return user


@router.post("/{username}/follow", status_code=status.HTTP_200_OK)
async def toggle_follow(
    username: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.username == username))
    target = result.scalar_one_or_none()

    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")
    if target.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="自分自身をフォローできません")

    existing = await db.execute(
        select(Follow).where(Follow.follower_id == current_user.id, Follow.followed_id == target.id)
    )
    follow = existing.scalar_one_or_none()

    if follow:
        await db.delete(follow)
        await db.commit()
        return {"following": False}
    else:
        db.add(Follow(follower_id=current_user.id, followed_id=target.id))
        await apply_score(db, target.id, "followed")
        await db.commit()
        return {"following": True}


@router.get("/{username}/followers", response_model=list[UserPublic])
async def get_followers(
    username: str,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")

    stmt = (
        select(User)
        .join(Follow, Follow.follower_id == User.id)
        .where(
            Follow.followed_id == user.id,
            User.score >= settings.SCORE_HIDDEN_THRESHOLD,
        )
        .offset(skip)
        .limit(limit)
    )
    followers = await db.execute(stmt)
    return followers.scalars().all()


@router.get("/{username}/following", response_model=list[UserPublic])
async def get_following(
    username: str,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")

    stmt = (
        select(User)
        .join(Follow, Follow.followed_id == User.id)
        .where(
            Follow.follower_id == user.id,
            User.score >= settings.SCORE_HIDDEN_THRESHOLD,
        )
        .offset(skip)
        .limit(limit)
    )
    following = await db.execute(stmt)
    return following.scalars().all()
