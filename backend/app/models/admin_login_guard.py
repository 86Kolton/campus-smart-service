from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AdminLoginGuard(Base):
    __tablename__ = "admin_login_guards"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    ip_address: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    user_agent_hash: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    first_failed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_failed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    lock_until: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_success_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
