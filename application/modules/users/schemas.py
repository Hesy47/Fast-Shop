from datetime import datetime

import jdatetime
from pydantic import BaseModel, field_serializer, field_validator, model_validator


class BasicLoginRequest(BaseModel):
    identifier: str
    password: str


class GetUserResponse(BaseModel):
    id: int
    username: str
    phone_number: str
    password: str
    user_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", mode="plain")
    def created_at_serializer(value: datetime):
        return str(jdatetime.datetime.fromgregorian(datetime=value))

    @field_serializer("updated_at", mode="plain")
    def updated_at_serializer(value: datetime):
        return str(jdatetime.datetime.fromgregorian(datetime=value))


class GetAllUsersResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[GetUserResponse]
