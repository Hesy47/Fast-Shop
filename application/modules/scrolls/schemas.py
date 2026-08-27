from datetime import datetime

import jdatetime
from pydantic import BaseModel, field_serializer

from application.modules.products.models import MenuType, ScrollType, StatusType


class GetScrollResponse(BaseModel):
    id: int
    title: str
    scroll: str
    link: str
    query: str
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at", mode="plain")
    def datetime_serializer(value: datetime):
        return str(jdatetime.datetime.fromgregorian(datetime=value))


class GetAllScrollsResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[GetScrollResponse]


class CreateScrollRequest(BaseModel):
    title: str
    scroll: str
    link: str
    query: str


class EditScrollRequest(BaseModel):
    title: str | None = None
    scroll: str | None = None
    link: str | None = None
    query: str | None = None


class PublicScrollProductGalleryResponse(BaseModel):
    id: int
    image: str


class PublicGetScrollProductResponse(BaseModel):
    id: int
    title: str
    price: int
    discounted_price: int
    discount_percent: str
    status: StatusType
    menu: MenuType
    scroll: ScrollType
    slug_tag: str | None
    title_tag: str | None
    description_tag: str | None
    collection_title: str
    gallery_set: list[PublicScrollProductGalleryResponse]


class PublicGetScrollProductsResponse(BaseModel):
    title: str
    scroll: str
    link: str
    query: str
    products: list[PublicGetScrollProductResponse]
