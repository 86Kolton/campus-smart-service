from sqlalchemy import BigInteger, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MessageNotification(Base):
    __tablename__ = "message_notifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    receiver_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_post_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    source_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content: Mapped[str] = mapped_column(String(255), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

