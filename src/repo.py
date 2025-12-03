from abc import ABC, abstractmethod

from src.abstractions import Student


class AbstractStudentRepo(ABC):
    @abstractmethod
    async def get_student_by_id[ConreteStudent: Student](
        self, tg_id: int
    ) -> ConreteStudent | None: ...

    @abstractmethod
    async def add_student[ConreteStudent: Student](
        self, student: ConreteStudent
    ) -> None: ...


class InMemoryRepo(AbstractStudentRepo):
    def __init__(self) -> None:
        self._students: list[Student] = []

    async def get_student_by_id(self, tg_id: int) -> Student | None:
        for student in self._students:
            if tg_id == student.tg_id:
                return student
        return None

    async def add_student(self, student: Student) -> None:
        self._students.append(student)
