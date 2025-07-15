from pydantic import BaseModel, field_validator, Field


class BaseCollectionsSchema(BaseModel):
    title: str
    id: int


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
        return value


class UpdateCollectionSchema(CreateCollectionSchema):
    pass


class DeleteCollectionSchema(BaseModel):
    title: str
