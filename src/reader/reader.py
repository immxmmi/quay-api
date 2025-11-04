import yaml
from pathlib import Path
from typing import Any, Dict, Type, TypeVar, Union

T = TypeVar("T")

def read_yaml(path: Union[str, Path]) -> Dict[str, Any]:
    """Reads a YAML file and returns a dict."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def read_yaml_as(path: Union[str, Path], model: Type[T]) -> T:
    """Reads a YAML file and parses it into a Pydantic model."""
    from pydantic import BaseModel
    data = read_yaml(path)
    if not issubclass(model, BaseModel):
        raise TypeError("Model must inherit from pydantic.BaseModel")
    return model(**data)

def read_yaml_live(path: Union[str, Path]) -> Dict[str, Any]:
    """Reads the YAML file fresh on every call for real-time updates."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)