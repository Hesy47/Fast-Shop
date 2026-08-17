from datetime import datetime

import jdatetime
from pydantic import BaseModel, RootModel, field_serializer


class GetSocialAppResponse(BaseModel):
    id: int
    title: str
    link: str
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at", mode="plain")
    def datetime_serializer(value: datetime):
        return str(jdatetime.datetime.fromgregorian(datetime=value))


class GetAllSocialAppsResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[GetSocialAppResponse]


class CreateSocialAppRequest(BaseModel):
    title: str
    link: str


class EditSocialAppRequest(BaseModel):
    title: str | None = None
    link: str | None = None


class PublicGetAllSocialAppsResponse(RootModel[dict[str, str]]):
    pass
