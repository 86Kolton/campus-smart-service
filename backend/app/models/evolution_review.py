from sqlalchemy import BigInteger, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class EvolutionReview(Base):
    __tablename__ = "evolution_reviews"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    kb_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    post_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    post_title: Mapped[str] = mapped_column(String(255), nullable=False)
    decision: Mapped[str] = mapped_column(String(32), nullable=False, default="reject")
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reviewer_model: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    reason: Mapped[str] = mapped_column(Text, nullable=False, default="")
    detail_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    document_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
