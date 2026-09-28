from datetime import datetime

import jdatetime
from pydantic import BaseModel, field_serializer

from application.modules.products.models import MenuType, ScrollType, StatusType


class PublicCollectionProductGalleryResponse(BaseModel):
    id: int
    image: str


class PublicCollectionProductResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    discounted_price: int
    discount_percent: str
    status: StatusType
    menu: MenuType
    scroll: ScrollType
    slug_tag: str | None
    title_tag: str | None
    description_tag: str | None
    canonical_tag: str | None
    collection_id: int
    collection_title: str
    sub_collection_id: int | None
    sub_collection_title: str | None
    gallery_set: list[PublicCollectionProductGalleryResponse]


class PublicCollectionResponse(BaseModel):
    id: int
    title: str
    image: str
    slug_tag: str | None
    title_tag: str | None
    description_tag: str | None
    canonical_tag: str | None


class PublicGetCollectionResponse(PublicCollectionResponse):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[PublicCollectionProductResponse]


class PublicGetAllCollectionsResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[PublicCollectionResponse]


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
