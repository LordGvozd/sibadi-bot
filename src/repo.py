

from abc import ABC, abstractmethod

from src.abstractions import Student


class AbstractStudentRepo(ABC):
    @abstractmethod 
    async def get_student_by_id[S: Student](self, tg_id: int) -> S | None: ...

    @abstractmethod 
    async def add_student[S: Student](self, student: S) -> None: ...


class InMemoryRepo(AbstractStudentRepo):
    def __init__(self) -> None:
        self._students: list[Student] = []

    async def get_student_by_id[S: Student](self, tg_id: int) -> S | None:
        for student in self._students:
            if tg_id == student.tg_id:
                return student
        return None
    
    async def add_student[S: Student](self, student: S) -> None:
        self._students.append(student)

