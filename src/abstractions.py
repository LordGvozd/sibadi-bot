from abc import ABC, ABCMeta, abstractmethod
from datetime import datetime, time
from enum import StrEnum, unique

import msgspec

from src.actions import ActionContainer
from src.models import Schedule


@unique
class InstitutionNames(StrEnum):
    SIBADI = "sibadi"


class StudentMeta(msgspec.StructMeta, ABCMeta): ...  # noqa: WPS604


class AbstarctStudent(msgspec.Struct, kw_only=True, metaclass=StudentMeta):
    tg_id: str
    institution_name: InstitutionNames


class ScheduleGetter[ConcreteStudent: AbstarctStudent](ABC):
    @abstractmethod
    async def get_day_schedule_for(
        self, student: ConcreteStudent, date: datetime
    ) -> Schedule | None: ...

    @abstractmethod
    async def get_week_schedule_for(
        self, student: ConcreteStudent, date: datetime
    ) -> list[Schedule] | None: ...


class Institution[ConcreteStudent: AbstarctStudent](ABC):
    @property
    @abstractmethod
    def name(self) -> InstitutionNames: ...

    @property
    @abstractmethod
    def schedule_getter(self) -> ScheduleGetter[ConcreteStudent]: ...

    @property
    @abstractmethod
    def get_timetable(self) -> tuple[tuple[time, time], ...]: ...

    @property
    @abstractmethod
    def action_container(self) -> ActionContainer: ...
