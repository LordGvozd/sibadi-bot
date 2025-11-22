"""Здесь основыные константы, например, ключи для словарей,
которые нужны для форматирования сообщений."""

from typing import Final, Literal

SCHEDULE_KEY: Final[Literal["schedule"]] = "schedule"
type ScheduleDictType = dict[Literal["schedule"], str]

TIME_INFO: Final[str] = """
1) 8:20 - 9:50
2) 10:00 - 11:30
3) 11:40 - 13:10
4) 13:45 - 15:15
5) 15:25 - 16:55
6) 17:05 - 18:35
"""
