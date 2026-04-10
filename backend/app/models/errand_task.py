from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ErrandTask(Base):
    __tablename__ = "errand_tasks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    publisher_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    runner_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    task_type: Mapped[str] = mapped_column(String(32), nullable=False, default="quick")
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    reward: Mapped[str] = mapped_column(String(32), nullable=False, default="￥5")
    eta: Mapped[str] = mapped_column(String(64), nullable=False, default="尽快")
    pickup_location: Mapped[str] = mapped_column(String(128), nullable=False)
    destination: Mapped[str] = mapped_column(String(128), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    contact: Mapped[str] = mapped_column(String(128), nullable=False, default="站内私信")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    accepted_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confirmed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
    canceled_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)
