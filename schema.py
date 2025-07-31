from typing import Optional
from pydantic import BaseModel, field_validator, PositiveInt
from dependencies import get_db_python
from models import Collection, Product


class BaseGetCollectionsSchema(BaseModel):
    id: int
    title: str


class GetCollectionSchema(BaseGetCollectionsSchema):
    pass


class GetAllCollectionsSchema(BaseModel):
    page: int
    per_page: int
    total_items: int
    has_next: bool
    has_previous: bool
    items: list[BaseGetCollectionsSchema]


class CreateCollectionSchema(BaseModel):
    title: str

    @field_validator("title")
    def title_validator(cls, value: str):
        if value.strip() == "":
            raise ValueError("the title field is required")

        if not value.isalnum():
            raise ValueError("please inter a valid title")

        with get_db_python() as db:
            unique_title = (
                db.query(Collection).filter(Collection.title == value).first()
            )

            if unique_title:
                raise ValueError("we already have this collection in our DataBase")

        return value


class UpdateCollectionSchema(BaseModel):
    title: Optional[str] = None

    @field_validator("title")
    def title_validator(cls, value: str):
        if value is None:
            return value

        if not value.isalnum():
            raise ValueError("please inter a valid title")

        with get_db_python() as db:
            unique_title = (
                db.query(Collection).filter(Collection.title == value).first()
            )

            if unique_title:
                raise ValueError("we already have this collection in our DataBase")

        return value


class DeleteCollectionSchema(BaseModel):
    pass


class BaseProductSchema(BaseModel):
    id: int
    title: str
    price: PositiveInt
    description: str
    menu: str
    collection_id: int
    image_path: str
    collection_title: str


class GetProductSchema(BaseProductSchema):
    pass


class GetAllProductsSchema(BaseModel):
    page: int
    per_page: int
    total_items: int
    has_next: bool
    has_previous: bool
    items: list[BaseProductSchema]


class CreateProductSchema(BaseModel):
    title: str
    price: PositiveInt
    description: str
    menu: str
    collection_id: int

    @field_validator("title")
    def title_validator(cls, value: str):
        if not value.isalnum():
            raise ValueError("please inter a valid title")

        with get_db_python() as db:
            unique_title = db.query(Product).filter(Product.title == value).first()

            if unique_title:
                raise ValueError("we already have this product in our DataBase")

        return value

    @field_validator("price")
    def price_validator(cls, value: int):
        if value >= 9999999999:
            raise ValueError("the range of price is not valid")

        if not isinstance(value, int):
            raise ValueError("price must be a integer field")
        return value

    @field_validator("menu")
    def menu_validator(cls, value: str):
        if value not in ("casual", "special"):
            raise ValueError("the menu choices are special and casual")
        return value

    @field_validator("collection_id")
    def collection_id_validator(cls, value: int):
        with get_db_python() as db:
            exist_collection = db.query(Product).filter(Product.id == value).first()

            if not exist_collection:
                raise ValueError("we do not have this collection in our DataBase")
        return value


class UpdateProductSchema(BaseModel):
    title: Optional[str] = None
    price: Optional[PositiveInt] = None
    description: Optional[str] = None
    menu: Optional[str] = None
    collection_id: Optional[int] = None

    @field_validator("title")
    def title_validator(cls, value: str):
        if value is None:
            return value

        if not value.isalnum():
            raise ValueError("please inter a valid title")

        with get_db_python() as db:
            unique_title = db.query(Product).filter(Product.title == value).first()

            if unique_title:
                raise ValueError("we already have this product in our DataBase")

        return value

    @field_validator("price")
    def price_validator(cls, value: int):
        if value is None:
            return value

        if value >= 9999999999:
            raise ValueError("the range of price is not valid")

        if not isinstance(value, int):
            raise ValueError("price must be a integer field")
        return value

    @field_validator("menu")
    def menu_validator(cls, value: str):
        if value is None:
            return value
        if value not in ("casual", "special"):
            raise ValueError("the menu choices are special and casual")
        return value

    @field_validator("collection_id")
    def collection_id_validator(cls, value: int):
        if value is None:
            return value

        with get_db_python() as db:
            exist_collection = db.query(Product).filter(Product.id == value).first()

            if not exist_collection:
                raise ValueError("we do not have this collection in our DataBase")

        return value
