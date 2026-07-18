from datetime import datetime

import jdatetime
from pydantic import BaseModel, field_serializer, field_validator, model_validator


class CreateCollectionRequest(BaseModel):
    title: str
    image: str


class EditCollectionRequest(BaseModel):
    title: str | None = None
    image: str | None = None
