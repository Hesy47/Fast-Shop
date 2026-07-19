from datetime import datetime

import jdatetime
from pydantic import BaseModel, field_serializer


class PublicGetSubCollectionResponse(BaseModel):
    id: int
    title: str
    image: str


class PublicGetAllSubCollectionsResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[PublicGetSubCollectionResponse]


class GetSubCollectionResponse(BaseModel):
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


class GetAllSubCollectionsResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[GetSubCollectionResponse]


class CreateSubCollectionRequest(BaseModel):
    title: str
    image: str


class EditSubCollectionRequest(BaseModel):
    title: str | None = None
    image: str | None = None
