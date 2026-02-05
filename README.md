# TinyCSP

TinyCSP is a tiny, educational constraint programming (CP) solver inspired by the MiniCP MOOC codebase and documentation. It is intentionally minimal to make the core ideas—domains, propagation, and depth‑first search—easy to read and extend.

Reference materials:
- https://github.com/minicp/minicp/tree/mooc/src/main/java/minicp
- http://www.minicp.org/

## Status

- Python backend: available now (`python/tinycsp`).
- Rust backend: available via `_core` extension (`src` + `maturin`), selectable at runtime.
- API surface: small and intentionally simple.

## Features

- Finite‑domain integer variables (`Domain`, `Variable`).
- Constraints: `not_equal`, `equal`, and `all_different` (pairwise decomposition).
- Simple fix‑point propagation.
- Depth‑first search with domain backup/restore.
- Two backends for DFS: pure Python or Rust.

## Installation (dev)

```bash
uv sync --locked
source .venv/bin/activate
maturin develop
```

## Quick Start

```python
from tinycsp import TinyCSP

csp = TinyCSP()

x = csp.make_variable(3)  # domain: {0,1,2}
y = csp.make_variable(3)

csp.not_equal(x, y)       # x != y

solutions = []

csp.dfs(lambda sol: solutions.append(sol))
print(solutions)
```

## Notebook Examples

Example notebooks live in `notebook/` (they are plain `.py` notebooks runnable with Python).

- `notebook/graph_cloring.py`: Japan prefecture graph coloring using GeoJSON + TinyCSP.
- `notebook/n_queen.py`: N‑Queens (uses `all_different` + diagonals) and can run with the Rust backend.
- `notebook/sudoku.py`: Sudoku solver with row/column/block constraints.

You can run them like:

```bash
python notebook/n_queen.py
```

## API Overview (TinyCSP)

Core methods (from `python/tinycsp/tinycsp.py`):

- `make_variable(n: int) -> Variable`:
  Creates a variable with domain `{0, 1, ..., n-1}`.
- `not_equal(x: Variable, y: Variable, offset: int = 0) -> None`:
  Adds `x != y + offset`.
- `equal(x: Variable, value: int) -> None`:
  Fixes `x == value`.
- `all_different(vars: list[Variable]) -> None`:
  Naive pairwise expansion into `not_equal` constraints.
- `dfs(on_solution, stop_after_first: bool = False, backend: "python"|"rust" = "python") -> bool`:
  Depth‑first search. `on_solution` receives a `tuple[int, ...]` in variable creation order.
  If `on_solution` returns `False`, search stops early.

## Backend Selection (Python vs Rust)

TinyCSP lets you choose the DFS backend per call:

```python
csp.dfs(on_solution, backend="python")
csp.dfs(on_solution, backend="rust")
```

- Default is `backend="python"`.
- Rust backend requires the `_core` extension built via `maturin develop`.
- Constraints supported by Rust backend mirror the Python ones (`equal`, `not_equal`, and `all_different` via decomposition).

## Project Layout

- `python/tinycsp`: Python implementation and public API.
- `src`: Rust extension module (via `pyo3`).
- `notebook`: Example notebooks / scripts.
- `pyproject.toml`: `maturin` build config and package metadata.


## Acknowledgements

This project is based on the ideas and structure of MiniCP and the associated MOOC materials for teaching constraint programming.

## License

MIT License. See `LICENSE`.
