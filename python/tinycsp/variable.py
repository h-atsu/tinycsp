from tinycsp.domain import Domain


class Variable:
    def __init__(self, n: int):
        self.dom = Domain(n)

    def __repr__(self) -> str:
        return f"Variable({self.dom})"
