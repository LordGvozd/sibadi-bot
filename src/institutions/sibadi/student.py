from src.abstractions import AbstarctStudent, InstitutionNames


class SibadiStudent(AbstarctStudent, kw_only=True):
    tg_id: str
    group_id: str  # type: ignore[misc]

    institution_name: InstitutionNames = InstitutionNames.SIBADI
