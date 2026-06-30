from datetime import datetime

import jdatetime
from pydantic import BaseModel, field_serializer, field_validator, model_validator

from application.modules.users.validators import CustomUserValidator
from application.core.hashers import CustomArgon2Hasher


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


class CreateUserRequest(BaseModel):
    username: str
    phone_number: str
    password: str
    user_type: str
    is_active: bool

    @field_validator("username", mode="after")
    def validate_username(value: str):
        value = value.strip()
        CustomUserValidator.username_validator(value)
        return value

    @field_validator("phone_number", mode="after")
    def validate_phone_number(value: str):
        value = value.strip()
        CustomUserValidator.phone_number_validator(value)
        return value

    @field_validator("password", mode="after")
    def validate_password(value: str):
        value = value.strip()
        CustomUserValidator.password_validator(value)
        return CustomArgon2Hasher.create_hashed_password_for_route(value)

    @field_validator("user_type", mode="after")
    def validate_user_type(value: str):
        value = value.strip()
        CustomUserValidator.user_type_validator(value)
        return value


class EditUserRequest(BaseModel):
    username: str | None = None
    phone_number: str | None = None
    password: str | None = None
    user_type: str | None = None
    is_active: bool | None = None

    @field_validator("username", mode="after")
    def validate_username(value: str | None):
        if value is None:
            return value

        CustomUserValidator.username_validator(value)
        value = value.strip()
        return value

    @field_validator("phone_number", mode="after")
    def validate_phone_number(value: str):
        if value is None:
            return value

        value = value.strip()
        CustomUserValidator.phone_number_validator(value)
        return value

    @field_validator("password", mode="after")
    def validate_password(value: str):
        if value is None:
            return value

        value = value.strip()
        CustomUserValidator.password_validator(value)
        return CustomArgon2Hasher.create_hashed_password_for_route(value)

    @field_validator("user_type", mode="after")
    def validate_user_type(value: str):
        if value is None:
            return value

        value = value.strip()
        CustomUserValidator.user_type_validator(value)
        return value
