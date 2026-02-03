from abc import ABC, abstractmethod

from tinycsp.variable import Variable


class Constraint(ABC):
    @abstractmethod
    def propagate(self) -> bool:
        pass


class NotEqualConstraint(Constraint):
    def __init__(self, x: Variable, y: Variable, offset: int = 0):
        self.x = x
        self.y = y
        self.offset = offset

    def propagate(self) -> bool:
        # Implement the propagation logic for not equal constraint
        if self.x.dom.is_fixed():
            return self.y.dom.remove(self.x.dom.min() - self.offset)
        elif self.y.dom.is_fixed():
            return self.x.dom.remove(self.y.dom.min() + self.offset)
        return False
