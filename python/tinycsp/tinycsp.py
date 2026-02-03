from collections.abc import Callable
from copy import deepcopy
from typing import TypeAlias

from tinycsp.constraint import Constraint, NotEqualConstraint
from tinycsp.domain import Domain
from tinycsp.exceptions import Inconsistency
from tinycsp.variable import Variable

Solution = tuple[int, ...]
OnSolutionCallback: TypeAlias = Callable[[Solution], None]


class TinyCSP:
    def __init__(self):
        self.n_recur: int = 0
        self.variables: list[Variable] = []
        self.constraints: list[Constraint] = []

    def make_variable(self, n: int) -> Variable:
        x = Variable(n)
        self.variables.append(x)
        return x

    def not_equal(self, x: Variable, y: Variable, offset: int = 0) -> None:
        self.constraints.append(NotEqualConstraint(x, y, offset))

    def fix_point(self) -> None:
        while True:
            changed = False
            for c in self.constraints:
                changed |= c.propagate()
            if not changed:
                return

    def backup_domains(self) -> list[Domain]:
        return [deepcopy(var.dom) for var in self.variables]

    def restore_domains(self, domains: list[Domain]) -> None:
        for var, domain in zip(self.variables, domains, strict=True):
            var.dom = domain

    def first_not_fixed(self) -> Variable | None:
        return next((var for var in self.variables if not var.dom.is_fixed()), None)

    def dfs(self, on_solution: OnSolutionCallback) -> None:
        self.n_recur += 1

        not_fixed_var = self.first_not_fixed()

        if not_fixed_var is None:
            # solution found
            solution = tuple(var.dom.min() for var in self.variables)
            on_solution(solution)

        else:
            val = not_fixed_var.dom.min()
            backup = self.backup_domains()

            # left branch: x = val
            try:
                not_fixed_var.dom.fix(val)
                self.fix_point()
                self.dfs(on_solution)
            except Inconsistency:
                pass

            self.restore_domains(backup)

            # right branch: x != val
            try:
                not_fixed_var.dom.remove(val)
                self.fix_point()
                self.dfs(on_solution)
            except Inconsistency:
                pass

        return
