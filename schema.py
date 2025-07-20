from pydantic import BaseModel, field_validator, PositiveFloat
from dependencies import get_db_python
from models import Collection


class BaseGetCollectionsSchema(BaseModel):
    title: str
    id: int


class GetCollectionSchema(BaseModel):
    item: BaseGetCollectionsSchema
    status: str


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
        if not value.isalnum():
            raise ValueError("please inter a valid collection")

        with get_db_python() as db:
            unique_title = (
                db.query(Collection).filter(Collection.title == value).first()
            )

            if unique_title:
                raise ValueError("we already have this collection in our DataBase")

        return value


class UpdateCollectionSchema(CreateCollectionSchema):
    pass


class DeleteCollectionSchema(BaseModel):
    title: str


class BaseProductSchema(BaseModel):
    id: int
    title: str
    price: PositiveFloat
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
