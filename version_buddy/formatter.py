from dataclasses import fields, Field, is_dataclass, asdict
from typing import Any, TextIO, Callable, Tuple
import json


DataclassFormatter = Callable[[ Any ], None]
DataclassFormatter.__doc__ = \
    """Formatters turn a dataclass into some kind of textual output. 

    A formatter is recommended to write all fields, but can of course skip some when it is 
    appropriate.

    Note: Formatters should not print a trailing newline.
    """

class JSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if is_dataclass(o):
            return asdict(o)
        
        return super().default(o)

def into_json(**kwargs) -> DataclassFormatter:
    """Creates a formatter that uses the built-in `json` module.
    
    Accepts the same arguments as `json.JSONEncoder`.
    """
    encoder = JSONEncoder(**kwargs)

    def process(data):
        return encoder.encode(data)

    return process