from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from application.core.database import Base

if TYPE_CHECKING:
    from application.modules.products.models import Product


class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        unique=True,
    )

    image: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        unique=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        server_default=func.now(),
        server_onupdate=func.now(),
    )

    products: Mapped[list[Product]] = relationship(
        "Product",
        back_populates="collection",
    )

    def __str__(self):
        return self.title
