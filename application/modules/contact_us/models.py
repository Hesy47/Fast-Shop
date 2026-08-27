from datetime import datetime

from application.core.database import Base
from sqlalchemy import BigInteger, DateTime, String, func, Text
from sqlalchemy.orm import Mapped, mapped_column


class ContactUs(Base):
    __tablename__ = "contact_us"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )

    phone_number: Mapped[str] = mapped_column(
        String(11),
        nullable=False,
    )

    subject: Mapped[str] = mapped_column(
        String(180),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
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
        return self.subject
