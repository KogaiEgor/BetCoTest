import time
import enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class EventState(enum.Enum):
    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3


class BaseEvent(BaseModel):
    coefficient: Optional[float] = Field(None, gt=0)
    deadline: Optional[int] = Field(None)
    state: Optional[EventState] = Field(None)

    @field_validator("coefficient")
    @classmethod
    def validate_coefficient(cls, value):
        if value is not None:
            if value <= 1:
                raise ValueError("Coefficient must be a number more than 1")
            return round(value, 2)
        raise ValueError("Coefficient must be a number with up to two decimal places")

    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, value):
        if value and value <= int(time.time()):
            raise ValueError("Deadline must be greater than the current time")
        return value


class Event(BaseEvent):
    event_id: str = Field(...)
    coefficient: float = Field(..., gt=0)
    deadline: int = Field(...)
    state: EventState = Field(...)


class CreateEvent(BaseEvent):
    coefficient: float = Field(..., gt=0)
    deadline: int = Field(...)
    state: EventState = Field(...)


class UpdateEvent(BaseEvent):
    pass
