from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.models.like import Like
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostCreate, PostRead, PostUpdate
from app.services.score_service import apply_score

router = APIRouter(prefix="/posts", tags=["posts"])


def _filter_visible_users(query):
    """スコアが閾値以上のユーザーの投稿のみ返す"""
    return query.join(User, Post.author_id == User.id).where(
        User.score >= settings.SCORE_HIDDEN_THRESHOLD
    )


@router.get("", response_model=list[PostRead])
async def list_posts(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """タイムライン: 優先表示ユーザーを先に、その後通常ユーザーの順で返す"""
    stmt = (
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.likes))
        .join(User, Post.author_id == User.id)
        .where(User.score >= settings.SCORE_HIDDEN_THRESHOLD)
        .order_by(
            (User.score >= settings.SCORE_PRIORITY_THRESHOLD).desc(),
            Post.created_at.desc(),
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    posts = result.scalars().all()

    return [_build_post_read(post, current_user.id) for post in posts]


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    body: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = Post(author_id=current_user.id, content=body.content)
    db.add(post)
    await db.flush()

    await apply_score(db, current_user.id, "post_created")
    await db.commit()
    await db.refresh(post)

    stmt = select(Post).options(selectinload(Post.author), selectinload(Post.likes)).where(Post.id == post.id)
    result = await db.execute(stmt)
    post = result.scalar_one()

    return _build_post_read(post, current_user.id)


@router.get("/{post_id}", response_model=PostRead)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.likes))
        .where(Post.id == post_id)
    )
    result = await db.execute(stmt)
    post = result.scalar_one_or_none()

    if not post or not post.author.is_visible:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="投稿が見つかりません")

    return _build_post_read(post, current_user.id)


@router.patch("/{post_id}", response_model=PostRead)
async def update_post(
    post_id: int,
    body: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="投稿が見つかりません")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="この投稿を編集する権限がありません")

    if body.content is not None:
        post.content = body.content

    await db.commit()
    await db.refresh(post)

    stmt = select(Post).options(selectinload(Post.author), selectinload(Post.likes)).where(Post.id == post.id)
    result = await db.execute(stmt)
    post = result.scalar_one()

    return _build_post_read(post, current_user.id)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="投稿が見つかりません")
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="この投稿を削除する権限がありません")

    await db.delete(post)
    await apply_score(db, post.author_id, "post_deleted")
    await db.commit()


@router.post("/{post_id}/like", status_code=status.HTTP_200_OK)
async def toggle_like(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="投稿が見つかりません")

    existing = await db.execute(
        select(Like).where(Like.user_id == current_user.id, Like.post_id == post_id)
    )
    like = existing.scalar_one_or_none()

    if like:
        await db.delete(like)
        await apply_score(db, post.author_id, "like_removed")
        await db.commit()
        return {"liked": False}
    else:
        db.add(Like(user_id=current_user.id, post_id=post_id))
        await apply_score(db, post.author_id, "like_received")
        await db.commit()
        return {"liked": True}


def _build_post_read(post: Post, current_user_id: int) -> PostRead:
    return PostRead(
        id=post.id,
        author_id=post.author_id,
        author=post.author,
        content=post.content,
        media_url=post.media_url,
        media_type=post.media_type,
        likes_count=len(post.likes),
        comments_count=0,
        is_liked=any(like.user_id == current_user_id for like in post.likes),
        created_at=post.created_at,
        updated_at=post.updated_at,
    )
