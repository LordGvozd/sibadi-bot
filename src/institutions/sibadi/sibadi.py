from datetime import datetime, time
from collections.abc import Sequence

import msgspec
from src.abstractions import Institution, Student, InstitutionNames, ScheduleGetter
from src.institutions.sibadi._parser import get_day_schedule, get_remain_week_schedule
from src.models import Schedule, Lesson


class SibadiStudent(msgspec.Struct):
    tg_id: str
    institution_name = InstitutionNames.SIBADI
    group_id: str


class SibadiScheduleGetter[S: SibadiStudent]:
    async def get_day_schedule_for(self, student: S, date: datetime) -> Schedule | None: 
        return get_day_schedule(student.group_id, date)
        
    
    async def get_week_schedule_for(self, student: S, date: datetime) -> list[Schedule] | None: 
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
        return (
            (time(8, 20), time(9, 50)),
            (time(10, 00), time(11, 30)),
            (time(11, 40), time(13, 10)),
            (time(13, 45), time(15, 15)),
            (time(15, 25), time(16, 55)),
            (time(17, 5), time(18, 35)),
        )

