
from dataclasses import dataclass

@dataclass(frozen=True)
class Action:
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    special: str | None = None
    promotion: str | None = None