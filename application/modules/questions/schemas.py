from datetime import datetime

import jdatetime
from pydantic import BaseModel, RootModel, field_serializer


class PublicQuestionResponse(BaseModel):
    question: str
    answer: str
    question_place: str


class PublicGetAllQuestionsResponse(RootModel[list[PublicQuestionResponse]]):
    pass


class GetQuestionResponse(PublicQuestionResponse):
    id: int
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at", mode="plain")
    def datetime_serializer(value: datetime):
        return str(jdatetime.datetime.fromgregorian(datetime=value))


class GetAllQuestionsResponse(BaseModel):
    count: int
    next: str | None
    previous: str | None
    total_pages: int
    current_page: int
    results: list[GetQuestionResponse]


class CreateQuestionRequest(BaseModel):
    question: str
    answer: str
    question_place: str


class EditQuestionRequest(BaseModel):
    question: str | None = None
    answer: str | None = None
    question_place: str | None = None
