# %%
import time

from tinycsp import TinyCSP

# %%
board: list[list[int]] = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 0, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 0],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [0, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 0],
]

# %%
csp = TinyCSP()
q = [[csp.make_variable(9) for _ in range(9)] for _ in range(9)]

for i in range(9):
    for j in range(9):
        if board[i][j] != 0:
            csp.equal(q[i][j], board[i][j] - 1)

for i in range(9):
    csp.all_different(q[i])  # rows
    csp.all_different([q[j][i] for j in range(9)])  # columns

for bi in range(3):
    for bj in range(3):
        block_vars = []
        for di in range(3):
            for dj in range(3):
                block_vars.append(q[bi * 3 + di][bj * 3 + dj])
        csp.all_different(block_vars)
# %%
start_time = time.time()
solutions = []
csp.dfs(lambda sol: solutions.append(sol))
end_time = time.time()
print(f"Found {len(solutions)} solutions in {end_time - start_time:.2f} seconds.")


# %%
def print_board(solution: tuple[int, ...]) -> None:
    if len(solution) != 81:
        raise ValueError(f"Expected 81 values, got {len(solution)}")
    for i in range(9):
        row_vals = []
        for j in range(9):
            v = solution[i * 9 + j]
            row_vals.append(str(v + 1))
        row_str = (
            " ".join(row_vals[0:3])
            + " | "
            + " ".join(row_vals[3:6])
            + " | "
            + " ".join(row_vals[6:9])
        )
        print(row_str)
        if i in (2, 5):
            print("------+-------+------")
    print()


# %%
print("Top 10 solutions:")
for i, sol in enumerate(solutions):
    if i >= 10:
        break
    print(f"Solution {i}:")
    print_board(sol)
# %%
