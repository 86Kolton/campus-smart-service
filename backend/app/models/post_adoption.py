from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PostAdoption(Base):
    __tablename__ = "post_adoptions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    post_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    post_title: Mapped[str] = mapped_column(String(255), nullable=False)
    post_author_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    post_author_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    adopted_comment_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    adopted_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    adopted_user_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    adopted_comment_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    adopted_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
