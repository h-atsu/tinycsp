from collections.abc import Callable
from copy import deepcopy
from typing import Literal, TypeAlias

from tinycsp import _core
from tinycsp.constraint import Constraint, EqualConstraint, NotEqualConstraint
from tinycsp.domain import Domain
from tinycsp.exceptions import Inconsistency
from tinycsp.variable import Variable

Solution = tuple[int, ...]
# Return False to stop search early; return None/True to continue.
OnSolutionCallback: TypeAlias = Callable[[Solution], bool | None]


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

    def equal(self, x: Variable, value: int) -> None:
        self.constraints.append(EqualConstraint(x, value))

    def all_different(self, vars: list[Variable]) -> None:
        # Note: this is a naive implementation with O(n^2) constraints.
        n = len(vars)
        for i in range(n):
            for j in range(i + 1, n):
                self.not_equal(vars[i], vars[j])

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

    def dfs(
        self,
        on_solution: OnSolutionCallback,
        *,
        stop_after_first: bool = False,
        backend: Literal["python", "rust"] = "python",
    ) -> bool:
        if backend == "python":
            return self.dfs_py(on_solution, stop_after_first=stop_after_first)
        elif backend == "rust":
            return self.dfs_rs(on_solution, stop_after_first=stop_after_first)
        else:
            raise ValueError(f"Unknown backend: {backend}")

    def dfs_rs(
        self, on_solution: OnSolutionCallback, *, stop_after_first: bool = False
    ) -> bool:
        ok, n_recur = _core.dfs_rs(
            self.variables,
            self.constraints,
            on_solution,
            stop_after_first,
        )
        self.n_recur = n_recur
        return ok

    def dfs_py(
        self, on_solution: OnSolutionCallback, *, stop_after_first: bool = False
    ) -> bool:
        self.n_recur += 1

        not_fixed_var = self.first_not_fixed()

        if not_fixed_var is None:
            # solution found
            solution = tuple(var.dom.min() for var in self.variables)
            should_continue = on_solution(solution)
            if stop_after_first:
                return False
            if should_continue is False:
                return False

        else:
            val = not_fixed_var.dom.min()
            backup = self.backup_domains()

            # left branch: x = val
            try:
                not_fixed_var.dom.fix(val)
                self.fix_point()
                if not self.dfs(on_solution, stop_after_first=stop_after_first):
                    self.restore_domains(backup)
                    return False
            except Inconsistency:
                pass

            self.restore_domains(backup)

            # right branch: x != val
            try:
                not_fixed_var.dom.remove(val)
                self.fix_point()
                if not self.dfs(on_solution, stop_after_first=stop_after_first):
                    self.restore_domains(backup)
                    return False
            except Inconsistency:
                pass

        return True
