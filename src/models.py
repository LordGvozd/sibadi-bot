"""Модели данных."""

from datetime import datetime
from pydantic import BaseModel


class Lesson(BaseModel):
    """Урок в расписании."""

    name: str
    number: int
    audience: str

    starts_at: datetime
    ends_at: datetime


class Schedule(BaseModel):
    """Модель расписания."""

    date: datetime

    lessons: list[Lesson]

    def __hash__(self) -> int:
        return hash(self.date)
