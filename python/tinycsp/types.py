from collections.abc import Callable
from typing import TypeAlias

Solution = tuple[int, ...]
OnSolutionCallback: TypeAlias = Callable[[Solution], None]
