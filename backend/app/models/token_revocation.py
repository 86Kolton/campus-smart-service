from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TokenRevocation(Base):
    __tablename__ = "token_revocations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    jti: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    token_type: Mapped[str] = mapped_column(String(32), nullable=False)
    revoked_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
