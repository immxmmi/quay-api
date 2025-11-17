import yaml
from pathlib import Path
from typing import Any, Dict, Type, TypeVar, Union, IO

T = TypeVar("T")

def read_yaml(source: Union[str, Path, IO]) -> Dict[str, Any]:
    if hasattr(source, "read"):
        return yaml.safe_load(source)
    with open(source, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def read_yaml_as(source: Union[str, Path, IO], model: Type[T]) -> T:
    from pydantic import BaseModel
    data = read_yaml(source)
    if not issubclass(model, BaseModel):
        raise TypeError("Model must inherit from pydantic.BaseModel")
    return model(**data)

def read_yaml_live(source: Union[str, Path, IO]) -> Dict[str, Any]:
    return read_yaml(source)