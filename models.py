from sqlalchemy import Column, BigInteger, String, Text
from sqlalchemy import DECIMAL, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import db_base
import enum


class Collection(db_base):
    __tablename__ = "collections"
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    title = Column(String(35), nullable=False, unique=True)
    products = relationship(
        "Product",
        back_populates="collection",
        cascade="all, delete-orphan",
    )


class ProductionMenuEnums(enum.Enum):
    CASUAL = "casual"
    SPECIAL = "special"


class Product(db_base):
    __tablename__ = "products"
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    title = Column(String(35), nullable=False, unique=True)
    price = Column(DECIMAL(10, 0), nullable=False)
    description = Column(Text(), nullable=False)
    image_path = Column(String(250), nullable=False)
    menu = Column(
        Enum(ProductionMenuEnums),
        nullable=False,
        default=ProductionMenuEnums.CASUAL,
    )
    collection_id = Column(BigInteger, ForeignKey("collections.id"), nullable=False)
    collection = relationship("Collection", back_populates="products")
