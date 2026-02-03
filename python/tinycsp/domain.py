from tinycsp.exceptions import Inconsistency


class Domain:
    def __init__(self, n: int):
        self.n = n
        self.values = set(range(n))

    def is_fixed(self) -> bool:
        return len(self.values) == 1

    def size(self) -> int:
        return len(self.values)

    def min(self) -> int:
        return min(self.values)

    def remove(self, value: int) -> bool:
        """Remove value v. Return True if changed."""
        if not 0 <= value < self.n:
            return False

        if value not in self.values:
            return False

        if self.values == {value}:
            raise Inconsistency()

        self.values.remove(value)
        return True

    def fix(self, value: int) -> bool:
        """Set domain to {v}. Return True if changed."""
        if value not in self.values:
            raise Inconsistency()

        if not self.is_fixed():
            self.values = {value}
            return True

        return False

    def __repr__(self) -> str:
        return f"Domain({sorted(self.values)})"
