from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    wechat_openid: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(128), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    password_salt: Mapped[str | None] = mapped_column(String(64), nullable=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="client")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
