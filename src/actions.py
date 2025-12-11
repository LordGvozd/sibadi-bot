from typing import Annotated, TypeAlias, Callable, Awaitable, Protocol, get_args, get_origin, runtime_checkable, ClassVar
from enum import Enum
import inspect

@runtime_checkable
class ActionCommandSync(Protocol):
    def __call__(self, *args: str) -> str: ...


class Action:
    RequiredRaram: ClassVar[str]  = "required_param"
    
    def __init__(self, action_id: str, command: ActionCommandSync) -> None: 
        self._action_id = action_id
        self._commad = command
    
    def get_required_params(self) -> list[str]: 
        """Возвращает запрашиваемые действием параметры. """
        all_required_param: list[str] = []
        annotations = inspect.get_annotations(test_action)
        annotations.pop("return")

        for arg_name, arg_type in annotations.items():
            if get_origin(arg_type) == Annotated:
                if Action.RequiredRaram in get_args(arg_type):
                    all_required_param.append(arg_name)

        return all_required_param
        

    def run_action(self, **params: str) -> str:
        """ Запускает действие, возвращает  его результат. """
        if list(params.keys()) != self.get_required_params():
            raise Exception("Not enoght params!")

        return self._commad(**params)



def test_action(name: Annotated[str, Action.RequiredRaram]) -> str: ...



if __name__ == "__main__":

    



