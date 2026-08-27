from datetime import datetime

import jdatetime
from pydantic import BaseModel, field_serializer, field_validator

from application.modules.contact_us.validators import CustomContactUsValidator


class GetContactUsResponse(BaseModel):
    id: int
    phone_number: str
    subject: str
    message: str
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at", mode="plain")
    def datetime_serializer(value: datetime):
        return str(jdatetime.datetime.fromgregorian(datetime=value))


class GetAllContactUsResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[GetContactUsResponse]


class CreateContactUsRequest(BaseModel):
    phone_number: str
    subject: str
    message: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str):
        CustomContactUsValidator.phone_number_validator(value)
        return value

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, value: str):
        CustomContactUsValidator.subject_validator(value)
        return value

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str):
        CustomContactUsValidator.message_validator(value)
        return value


class PublicCreateContactUsRequest(CreateContactUsRequest):
    pass


class EditContactUsRequest(BaseModel):
    phone_number: str | None = None
    subject: str | None = None
    message: str | None = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str | None):
        if value is not None:
            CustomContactUsValidator.phone_number_validator(value)
        return value

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, value: str | None):
        if value is not None:
            CustomContactUsValidator.subject_validator(value)
        return value

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str | None):
        if value is not None:
            CustomContactUsValidator.message_validator(value)
        return value
