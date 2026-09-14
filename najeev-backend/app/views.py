from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class NoteInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=50000)


class NoteView(NoteInput):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime


class TokenView(BaseModel):
    access_token: str
    token_type: str = 'bearer'
