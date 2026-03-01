from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.message import Message
from app.models.user import User
from app.schemas.message import MessageCreate, MessageRead

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("", response_model=list[MessageRead])
async def list_messages(
    other_user_id: int,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(Message)
        .where(
            or_(
                (Message.sender_id == current_user.id) & (Message.receiver_id == other_user_id),
                (Message.sender_id == other_user_id) & (Message.receiver_id == current_user.id),
            )
        )
        .order_by(Message.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def send_message(
    body: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.id == body.receiver_id))
    receiver = result.scalar_one_or_none()
    if not receiver or not receiver.is_visible:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="送信先ユーザーが見つかりません")

    message = Message(
        sender_id=current_user.id,
        receiver_id=body.receiver_id,
        content=body.content,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


@router.patch("/{message_id}/read", status_code=status.HTTP_200_OK)
async def mark_read(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Message).where(Message.id == message_id, Message.receiver_id == current_user.id)
    )
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="メッセージが見つかりません")

    message.is_read = True
    await db.commit()
    return {"ok": True}
