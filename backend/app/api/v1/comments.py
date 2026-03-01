from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentRead
from app.services.score_service import apply_score

router = APIRouter(prefix="/posts/{post_id}/comments", tags=["comments"])


@router.get("", response_model=list[CommentRead])
async def list_comments(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Comment)
        .options(selectinload(Comment.author), selectinload(Comment.replies))
        .where(Comment.post_id == post_id, Comment.parent_id.is_(None))
        .order_by(Comment.created_at.asc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    body: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="投稿が見つかりません")

    comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        content=body.content,
        parent_id=body.parent_id,
    )
    db.add(comment)
    await db.flush()

    if post.author_id != current_user.id:
        await apply_score(db, post.author_id, "comment_received")

    await db.commit()
    await db.refresh(comment)

    stmt = select(Comment).options(selectinload(Comment.author)).where(Comment.id == comment.id)
    result = await db.execute(stmt)
    return result.scalar_one()


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    post_id: int,
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id, Comment.post_id == post_id))
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="コメントが見つかりません")
    if comment.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="削除する権限がありません")

    await db.delete(comment)
    await db.commit()
