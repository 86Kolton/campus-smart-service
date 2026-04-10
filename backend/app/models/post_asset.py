from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PostAsset(Base):
    __tablename__ = "post_assets"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    post_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    mime_type: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    public_url: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
