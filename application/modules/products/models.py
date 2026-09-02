from datetime import datetime
from enum import Enum as PythonEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from application.core.database import Base

if TYPE_CHECKING:
    from application.modules.collections.models import Collection
    from application.modules.sub_collections.models import SubCollection


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

    status: Mapped[str] = mapped_column(
        Enum(StatusType),
        nullable=False,
        default=StatusType.available,
    )

    menu: Mapped[str] = mapped_column(
        Enum(MenuType),
        nullable=False,
        default=MenuType.casual,
    )

    scroll: Mapped[str] = mapped_column(
        Enum(ScrollType),
        nullable=False,
        default=ScrollType.none,
    )
    slug_tag: Mapped[str] = mapped_column(
        String(200),
        nullable=True,
        unique=True,
    )

    title_tag: Mapped[str] = mapped_column(
        String(200),
        nullable=True,
    )

    description_tag: Mapped[str] = mapped_column(
        String(200),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        server_default=func.now(),
    )

    collection_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=False,
    )

    sub_collection_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("sub_collections.id", ondelete="SET NULL"),
        nullable=True,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        server_default=func.now(),
        server_onupdate=func.now(),
    )

    collection: Mapped["Collection"] = relationship(
        "Collection",
        back_populates="products",
    )

    sub_collection: Mapped["SubCollection"] = relationship(
        "SubCollection",
        back_populates="products",
    )

    images: Mapped[list["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
    )

    information: Mapped[list["ProductInformation"]] = relationship(
        "ProductInformation",
        back_populates="product",
    )

    def __str__(self):
        return self.title


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )

    image: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        unique=True,
    )

    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
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

    product: Mapped[Product] = relationship(
        "Product",
        back_populates="images",
    )

    def __str__(self):
        return self.image


class ProductInformation(Base):
    __tablename__ = "product_information"
    __table_args__ = (
        UniqueConstraint(
            "key",
            "product_id",
            name="uq_product_information_key_product_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )

    key: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    value: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
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

    product: Mapped[Product] = relationship(
        "Product",
        back_populates="information",
    )
