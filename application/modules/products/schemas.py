from datetime import datetime

import jdatetime
from pydantic import BaseModel, field_serializer, field_validator

from application.modules.products.models import MenuType, ScrollType, StatusType


class PublicProductInformationResponse(BaseModel):
    id: int
    key: str
    value: str


class PublicProductGalleryResponse(BaseModel):
    id: int
    image: str


class PublicGetProductResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    discounted_price: int
    discount_percent: int
    status: StatusType
    menu: MenuType
    scroll: ScrollType
    slug_tag: str | None
    title_tag: str | None
    description_tag: str | None
    canonical_tag: str | None
    collection_id: int
    sub_collection_id: int | None
    product_information: list[PublicProductInformationResponse]
    gallery_set: list[PublicProductGalleryResponse]


class PublicGetAllProductsResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[PublicGetProductResponse]


class SpecialGetProductResponse(PublicGetProductResponse):
    pass


class SpecialGetAllProductsResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[SpecialGetProductResponse]


class GetProductResponse(BaseModel):
    id: int
    title: str
    description: str
    price: int
    discounted_price: int
    discount_percent: int
    status: StatusType
    menu: MenuType
    scroll: ScrollType
    slug_tag: str | None
    title_tag: str | None
    description_tag: str | None
    canonical_tag: str | None
    collection_id: int
    sub_collection_id: int | None
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", mode="plain")
    def created_at_serializer(value: datetime):
        return str(jdatetime.datetime.fromgregorian(datetime=value))

    @field_serializer("updated_at", mode="plain")
    def updated_at_serializer(value: datetime):
        return str(jdatetime.datetime.fromgregorian(datetime=value))


class GetAllProductsResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[GetProductResponse]


class CreateProductRequest(BaseModel):
    title: str
    description: str
    price: int
    discounted_price: int
    status: StatusType = StatusType.available
    menu: MenuType = MenuType.casual
    scroll: ScrollType = ScrollType.none
    slug_tag: str
    title_tag: str | None = None
    description_tag: str | None = None
    collection_id: int
    sub_collection_id: int | None = None


class EditProductRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    price: int | None = None
    discounted_price: int | None = None
    status: StatusType | None = None
    menu: MenuType | None = None
    scroll: ScrollType | None = None
    slug_tag: str | None = None
    title_tag: str | None = None
    description_tag: str | None = None
    collection_id: int | None = None
    sub_collection_id: int | None = None

    @field_validator("collection_id")
    @classmethod
    def collection_id_must_not_be_null(cls, value: int | None):
        if value is None:
            raise ValueError("Collection id cannot be null")
        return value


class GetProductImageResponse(BaseModel):
    id: int
    image: str
    product_id: int
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", mode="plain")
    def created_at_serializer(value: datetime):
        return str(jdatetime.datetime.fromgregorian(datetime=value))

    @field_serializer("updated_at", mode="plain")
    def updated_at_serializer(value: datetime):
        return str(jdatetime.datetime.fromgregorian(datetime=value))


class GetAllProductImagesResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[GetProductImageResponse]


class CreateProductImageRequest(BaseModel):
    image: str
    product_id: int


class EditProductImageRequest(BaseModel):
    image: str | None = None
    product_id: int | None = None


class GetProductInformationResponse(BaseModel):
    id: int
    key: str
    value: str
    product_id: int
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", mode="plain")
    def created_at_serializer(value: datetime):
        return str(jdatetime.datetime.fromgregorian(datetime=value))

    @field_serializer("updated_at", mode="plain")
    def updated_at_serializer(value: datetime):
        return str(jdatetime.datetime.fromgregorian(datetime=value))


class GetAllProductInformationResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[GetProductInformationResponse]


class CreateProductInformationRequest(BaseModel):
    key: str
    value: str
    product_id: int


class EditProductInformationRequest(BaseModel):
    key: str | None = None
    value: str | None = None
    product_id: int | None = None
