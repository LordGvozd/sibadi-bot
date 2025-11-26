from enum import StrEnum, unique
from datetime import datetime, time
from abc import ABC, abstractmethod
from typing import Protocol, Sequence, runtime_checkable

from msgspec import Struct

from src.institutions.sibadi._parser import get_day_schedule
from src.models import *


@unique
class InstitutionNames(StrEnum):
    SIBADI = "sibadi"


@runtime_checkable
class Student(Protocol):
    tg_id: str
    institution_name: InstitutionNames

@runtime_checkable
class ScheduleGetter[S: Student](Protocol): 
    async def get_day_schedule_for(self, student: S, date: datetime) -> Schedule | None: ...
    
    async def get_week_schedule_for(self, student: S, date: datetime) -> list[Schedule] | None: ...


class Institution[S: Student](ABC):
    @property
    @abstractmethod 
    def name(self) -> InstitutionNames: ...

    @property
    @abstractmethod
    def schedule_getter(self) -> ScheduleGetter[S]: ...

    @property
    @abstractmethod 
    def get_timetable(self) -> Sequence[tuple[time, time]]: ...





