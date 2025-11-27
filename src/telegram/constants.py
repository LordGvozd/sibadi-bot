"""Здесь основыные константы, например, ключи для словарей,
которые нужны для форматирования сообщений."""

from typing import Final, Literal

SCHEDULE_KEY: Final[Literal["schedule"]] = "schedule"
type ScheduleDictType = dict[Literal["schedule"], str]
