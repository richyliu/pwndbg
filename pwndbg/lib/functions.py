from __future__ import annotations

from typing import List
from typing import NamedTuple


class Function(NamedTuple):
    type: str
    derefcnt: int
    name: str
    args: List[Argument]


class Argument(NamedTuple):
    type: str
    derefcnt: int
    name: str
