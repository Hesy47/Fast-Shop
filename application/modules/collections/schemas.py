from datetime import datetime

import jdatetime
from pydantic import BaseModel, field_serializer, field_validator, model_validator


class PublicGetCollectionResponse(BaseModel):
    id: int
    title: str
    image: str


class PublicGetAllCollectionsResponse(BaseModel):
    next: str | None
    previous: str | None
    current_page: int
    results: list[PublicGetCollectionResponse]


class GetCollectionResponse(BaseModel):
    id: int
    title: str
    image: str
    created_at: datetime
    updated_at: datetime


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
