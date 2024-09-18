from typing import Mapping, Sequence
from dataclasses import dataclass
from io import StringIO

from version_buddy import formatter


def test_into_json():
    @dataclass
    class Nonsense:
        seq: list
        mapping: dict

        integer: int = 3
        text: str = "hello"

    json_formatter = formatter.into_json()
    
    result = json_formatter(Nonsense(seq=[1,2], mapping={ "a": "b" }))

    assert """{"seq": [1, 2], "mapping": {"a": "b"}, "integer": 3, "text": "hello"}""" == result
