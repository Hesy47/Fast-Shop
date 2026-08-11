from datetime import datetime

import jdatetime
from pydantic import BaseModel, field_serializer


class PublicBannerResponse(BaseModel):
    id: int
    title: str
    image: str


class PublicDesktopBannerResponse(PublicBannerResponse):
    pass


class PublicPhoneBannerResponse(PublicBannerResponse):
    pass


class PublicGetAllDesktopBannersResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[PublicDesktopBannerResponse]


class PublicGetAllPhoneBannersResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[PublicPhoneBannerResponse]


class GetBannerResponse(PublicBannerResponse):
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at", mode="plain")
    def datetime_serializer(value: datetime):
        return str(jdatetime.datetime.fromgregorian(datetime=value))


class GetDesktopBannerResponse(GetBannerResponse):
    pass


class GetPhoneBannerResponse(GetBannerResponse):
    pass


class GetAllDesktopBannersResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[GetDesktopBannerResponse]


class GetAllPhoneBannersResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[GetPhoneBannerResponse]


class CreateBannerRequest(BaseModel):
    title: str
    image: str


class CreateDesktopBannerRequest(CreateBannerRequest):
    pass


class CreatePhoneBannerRequest(CreateBannerRequest):
    pass


class EditBannerRequest(BaseModel):
    title: str | None = None
    image: str | None = None


class EditDesktopBannerRequest(EditBannerRequest):
    pass


class EditPhoneBannerRequest(EditBannerRequest):
    pass
