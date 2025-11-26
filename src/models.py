"""Модели данных."""

from datetime import datetime
from typing import override

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

    @override
    def __hash__(self) -> int:
        """Хэширует расписание по урокам, необходим для кэша."""
        # ToDo: Make normal hash function
        return hash(self.date)


