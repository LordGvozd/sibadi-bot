from datetime import datetime, time

import msgspec

from src.abstractions import (
    Institution,
    InstitutionNames,
    ScheduleGetter,
)
from src.institutions.sibadi._parser import (
    get_day_schedule,
    get_remain_week_schedule,
)
from src.models import Schedule


class SibadiStudent(msgspec.Struct):
    tg_id: str
    institution_name = InstitutionNames.SIBADI
    group_id: str


class SibadiScheduleGetter:
    async def get_day_schedule_for(
        self, student: SibadiStudent, date: datetime
    ) -> Schedule | None:
        return get_day_schedule(student.group_id, date)

    async def get_week_schedule_for(
        self, student: SibadiStudent, date: datetime
    ) -> list[Schedule] | None:
        return get_remain_week_schedule(student.group_id, date)


class Sibadi[S: SibadiStudent](Institution[SibadiStudent]):
    @property
    def name(self) -> InstitutionNames:
        return InstitutionNames.SIBADI

    @property
    def schedule_getter(self) -> ScheduleGetter[S]:
        return SibadiScheduleGetter()

    @property
    def get_timetable(self) -> tuple[tuple[time, time], ...]:
        return (  # noqa: WPS227
            (time(8, 20), time(9, 50)),  # noqa: WPS432
            (time(10, 00), time(11, 30)),  # noqa: WPS432
            (time(11, 40), time(13, 10)),  # noqa: WPS432
            (time(13, 45), time(15, 15)),  # noqa: WPS432
            (time(15, 25), time(16, 55)),  # noqa: WPS432
            (time(17, 5), time(18, 35)),  # noqa: WPS432
        )
