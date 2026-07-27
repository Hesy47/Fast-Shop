from datetime import datetime
from enum import Enum as PythonEnum

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from application.core.database import Base


class UserType(str, PythonEnum):
    admin = "admin"
    customer = "customer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )

    username: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
        unique=True,
    )

    phone_number: Mapped[str] = mapped_column(
        String(11),
        nullable=False,
        unique=True,
        index=True,
    )

    password: Mapped[str] = mapped_column(
        String(250),
        nullable=False,
    )

    user_type: Mapped[str] = mapped_column(
        Enum(UserType),
        nullable=False,
        default=UserType.customer,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
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
        return self.username
