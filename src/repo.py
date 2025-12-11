from abc import ABC, abstractmethod
from typing import override

from src.abstractions import AbstarctStudent


class AbstractStudentRepo(ABC):
    @abstractmethod
    async def get_student_by_id[ConreteStudent: AbstarctStudent](
        self, tg_id: int
    ) -> AbstarctStudent | None: ...

    @abstractmethod
    async def add_student[ConreteStudent: AbstarctStudent](
        self, student: AbstarctStudent
    ) -> None: ...


class InMemoryRepo(AbstractStudentRepo):
    def __init__(self) -> None:
        self._students: list[AbstarctStudent] = []

    @override
    async def get_student_by_id(self, tg_id: int) -> AbstarctStudent | None:
        for student in self._students:
            if str(tg_id) == student.tg_id:
                return student
        return None

    @override
    async def add_student(self, student: AbstarctStudent) -> None:
        self._students.append(student)
