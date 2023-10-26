import uuid
from typing import Optional, Annotated
from datetime import datetime as dt

from pydantic import BaseModel, Field, ConfigDict, field_serializer

TIME_FORMAT = '%d.%m.%Y %H:%M:%S.%f'


#  Default response model
class DefaultResponse(BaseModel):
    success: bool
    error: Optional[Annotated[str, Field(...)]] = None


#  Simple book model
class Book(BaseModel):
    title: str
    text: str
    datetime: dt = Field(default_factory=dt.utcnow)


#  Broker book model
class BrokerBook(Book):
    model_config = ConfigDict(from_attributes=True)

    @field_serializer('title', check_fields=False)
    def serialize_title(self, title: str, _info):
        return title.encode('utf-8')

    @field_serializer('text', check_fields=False)
    def serialize_text(self, text: str, _info):
        return text.encode('utf-8')


#  Book model for ORM
class BaseBook(Book):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    x_avg_count_in_line: Optional[Annotated[float, Field(...)]] = None


#  `/list` book model
class ReadBook(BaseModel):
    title: str
    x_avg_count_in_line: float
    datetime: dt

    @field_serializer('x_avg_count_in_line', check_fields=False)
    def serialize_x_avg_count_in_line(self, x_avg_count_in_line: float, _info):
        return round(x_avg_count_in_line, 3)

    @field_serializer('datetime', check_fields=False)
    def serialize_datetime(self, datetime: dt, _info):
        return datetime.strftime(TIME_FORMAT)[:-3]
