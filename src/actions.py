import functools
import inspect
from collections.abc import Sequence
from dataclasses import dataclass
from typing import (
    Annotated,
    Any,
    Protocol,
    get_args,
    get_origin,
    runtime_checkable,
)


@runtime_checkable
class ActionCommandSync(Protocol):
    def __call__(self, *args: str) -> str: ...


@dataclass
class BaseParam:
    display_name: str

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.display_name}"


@dataclass
class TextParam(BaseParam): ...


@dataclass
class TextFromCollectionParam(BaseParam):
    """Value of this param must be in collection."""

    collection: Sequence[str]


@dataclass
class ChoiceParam(BaseParam):
    """Value of this param choosing from list."""

    variants: Sequence[str]


class RequireStudent: ...


Param = TextParam | TextFromCollectionParam | ChoiceParam


class Action:
    def __init__(self, display_name: str, command: ActionCommandSync) -> None:
        self.command = command
        self.display_name = display_name

    def get_params(self) -> dict[str, Param]:
        """Возвращает запрашиваемые действием параметры, которые должен предоставить пользователь."""
        all_required_param: dict[str, Param] = {}
        annotations = inspect.get_annotations(self.command)

        if "return" in annotations:
            annotations.pop("return")

        for hint_name, hint_type in annotations.items():
            if get_origin(hint_type) == Annotated:
                for arg in get_args(hint_type):
                    if isinstance(arg, Param):
                        all_required_param[hint_name] = arg

        return all_required_param

    def get_required_params(self) -> dict[str, RequireStudent]:
        """Возвращает параметры, которые должны быть предоставлены автоматически."""
        all_required_param: dict[str, RequireStudent] = {}
        annotations = inspect.get_annotations(self.command)

        if "return" in annotations:
            annotations.pop("return")

        for hint_name, hint_type in annotations.items():
            if get_origin(hint_type) == Annotated:
                for arg in get_args(hint_type):
                    if isinstance(arg, RequireStudent):
                        all_required_param[hint_name] = arg

        return all_required_param

    def run_action(self, **params: str) -> str:
        """Запускает действие, возвращает  его результат."""
        all_needed_params = list(self.get_params().keys()) + list(
            self.get_required_params().keys()
        )

        if sorted(params.keys()) != sorted(all_needed_params):
            raise Exception(
                str(all_needed_params) + " ||| " + str(list(params.keys()))
            )

        return self.command(**params)


class ActionContainer:
    def __init__(self) -> None:
        self._actions: dict[str, Action] = {}

    @property
    def actions(self) -> dict[str, Action]:
        return self._actions

    def get_action(self, action_id: str) -> Action | None:
        return self._actions.get(action_id, None)

    def action(self, *, action_id: str, display_name: str) -> Any:
        def decorator(func: ActionCommandSync):
            if action_id in self._actions:
                raise ValueError(
                    "Cant add action with same id to one container!"
                )
            self._actions[action_id] = Action(
                display_name=display_name, command=func
            )

            @functools.wraps
            def wrapped(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapped

        return decorator
