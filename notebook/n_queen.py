# %%
import time

from tinycsp import TinyCSP

# %%
n = 8
csp = TinyCSP()
q = [csp.make_variable(n) for _ in range(n)]

csp.all_different(q)

for i in range(n):
    for j in range(i + 1, n):
        csp.not_equal(q[i], q[j], j - i)
        csp.not_equal(q[i], q[j], i - j)

# %%
start_time = time.time()
solutions = []
csp.dfs(lambda sol: solutions.append(sol))
end_time = time.time()
print(f"Found {len(solutions)} solutions in {end_time - start_time:.2f} seconds.")


# %%
def print_board(solution: tuple[int, ...]) -> None:
    n = len(solution)
    for i in range(n):
        row = ""
        for j in range(n):
            if solution[i] == j:
                row += "Q "
            else:
                row += ". "
        print(row)
    print()


# %%
print("Top 10 solutions:")
for i, sol in enumerate(solutions):
    if i >= 10:
        break
    print(f"Solution {i}:")
    print_board(sol)
# %%
