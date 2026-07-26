from datetime import datetime
from enum import Enum as PythonEnum

from sqlalchemy import BigInteger, DateTime, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from application.core.database import Base


class StatusType(str, PythonEnum):
    available = "available"
    not_available = "not_available"


class MenuType(str, PythonEnum):
    casual = "casual"
    special = "special"


class ScrollType(str, PythonEnum):
    none = "none"
    scroll_1 = "scroll_1"
    scroll_2 = "scroll_2"
    scroll_3 = "scroll_3"
    scroll_4 = "scroll_4"


class Product(Base):
    __tablename__ = "products"

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

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    price: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    discounted_price: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
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

    def __str__(self):
        return self.title
