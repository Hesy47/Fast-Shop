from datetime import datetime

import jdatetime
from pydantic import BaseModel, field_serializer


class PublicGetCollectionResponse(BaseModel):
    id: int
    title: str
    image: str


class PublicGetAllCollectionsResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[PublicGetCollectionResponse]


class GetCollectionResponse(BaseModel):
    id: int
    title: str
    image: str
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", mode="plain")
    def created_at_serializer(value: datetime):
        return str(jdatetime.datetime.fromgregorian(datetime=value))

    @field_serializer("updated_at", mode="plain")
    def updated_at_serializer(value: datetime):
        return str(jdatetime.datetime.fromgregorian(datetime=value))


class GetAllCollectionsResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[GetCollectionResponse]


class CreateCollectionRequest(BaseModel):
    title: str
    image: str


class EditCollectionRequest(BaseModel):
    title: str | None = None
    image: str | None = None
