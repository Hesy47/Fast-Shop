from pydantic import BaseModel, field_validator
from dependencies import get_db_python
from models import Collection


class BaseCollectionsSchema(BaseModel):
    title: str
    id: int


class GetCollection(BaseModel):
    item: BaseCollectionsSchema
    status: str


class GetAllCollectionsSchema(BaseModel):
    page: int
    per_page: int
    total_items: int
    has_next: bool
    has_previous: bool
    items: list[BaseCollectionsSchema]


class CreateCollectionSchema(BaseModel):
    title: str

    @field_validator("title")
    def title_validator(cls, value: str):
        if not value.isalnum():
            raise ValueError("please inter a valid collection")

        with get_db_python() as db:
            unique_title = (
                db.query(Collection).filter(Collection.title == value).exists()
            )

            if unique_title:
                raise ValueError("we already have this collection in our DataBase")

        return value


class UpdateCollectionSchema(CreateCollectionSchema):
    pass


class DeleteCollectionSchema(BaseModel):
    title: str
