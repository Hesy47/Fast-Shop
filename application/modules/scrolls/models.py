from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from application.core.database import Base


class Scroll(Base):
    __tablename__ = "scrolls"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        unique=True,
    )

    scroll: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        unique=True,
    )

    link: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    query: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def str(self) -> str:
        return self.title
