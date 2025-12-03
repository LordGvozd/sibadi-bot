from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime, time
from enum import StrEnum, unique
from typing import Protocol, runtime_checkable

from src.models import Schedule


@unique
class InstitutionNames(StrEnum):
    SIBADI = "sibadi"


@runtime_checkable
class Student(Protocol):
    tg_id: str
    institution_name: InstitutionNames


@runtime_checkable
class ScheduleGetter[ConcreteStudent: Student](Protocol):
    async def get_day_schedule_for(
        self, student: ConcreteStudent, date: datetime
    ) -> Schedule | None: ...

    async def get_week_schedule_for(
        self, student: ConcreteStudent, date: datetime
    ) -> list[Schedule] | None: ...


class Institution[ConcreteStudent: Student](ABC):
    @property
    @abstractmethod
    def name(self) -> InstitutionNames: ...

    @property
    @abstractmethod
    def schedule_getter(self) -> ScheduleGetter[ConcreteStudent]: ...

    @property
    @abstractmethod
    def get_timetable(self) -> Sequence[tuple[time, time]]: ...
