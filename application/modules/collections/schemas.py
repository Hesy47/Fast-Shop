from datetime import datetime

import jdatetime
from pydantic import BaseModel, field_serializer


class PublicGetCollectionResponse(BaseModel):
    id: int
    title: str
    image: str
    slug_tag: str | None
    title_tag: str | None
    description_tag: str | None
    canonical_tag: str | None


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
    slug_tag: str | None
    title_tag: str | None
    description_tag: str | None
    canonical_tag: str | None
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
    slug_tag: str
    title_tag: str | None = None
    description_tag: str | None = None


class EditCollectionRequest(BaseModel):
    title: str | None = None
    image: str | None = None
    slug_tag: str | None = None
    title_tag: str | None = None
    description_tag: str | None = None
