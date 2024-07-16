from dataclasses import dataclass
from typing import Any, List, TypeVar, Callable, Type, cast

T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class RecentProjectElement:
    project_name: str
    project_path: str

    def __init__(self, name: str, path: str):
        self.project_name = name
        self.project_path = path

    @staticmethod
    def from_dict(obj: Any) -> 'RecentProjectElement':
        assert isinstance(obj, dict)
        project_name = obj.get("projectName")
        project_path = obj.get("projectPath")
        return RecentProjectElement(project_name, project_path)

    def to_dict(self) -> dict:
        result: dict = {"projectName": self.project_name,
                        "projectPath": self.project_path}
        return result


def recent_file_from_dict(s: Any) -> List[RecentProjectElement]:
    return from_list(RecentProjectElement.from_dict, s)


def recent_file_to_dict(x: List[RecentProjectElement]) -> Any:
    return from_list(lambda x: to_class(RecentProjectElement, x), x)
