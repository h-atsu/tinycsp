# TinyCSP

TinyCSP is a tiny, educational constraint programming (CP) solver inspired by the MiniCP MOOC codebase and documentation. It is intentionally minimal to make the core ideas—domains, propagation, and depth‑first search—easy to read and extend.

Reference materials:
- https://github.com/minicp/minicp/tree/mooc/src/main/java/minicp
- http://www.minicp.org/

This repository currently ships a pure‑Python implementation and is set up to migrate the core search engine to Rust for speed using `maturin` + `pyo3`.

## Status

- Python implementation: available now (`python/tinycsp`).
- Rust core: scaffolded (`src/lib.rs`), migration planned.
- API surface: small and intentionally simple.

## Features (current)

- Finite‑domain integer variables (`Domain`, `Variable`).
- Not‑equal constraint with optional offset.
- Simple fix‑point propagation.
- Depth‑first search with domain backup/restore.

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

## Project Layout

- `python/tinycsp`: Python implementation and public API.
- `src`: Rust extension module (via `pyo3`).
- `pyproject.toml`: `maturin` build config and package metadata.

## Roadmap

- Port core search and propagation to Rust.
- Expand constraint set (e.g., `all_different`, linear constraints).
- Add examples and benchmarks.

## Acknowledgements

This project is based on the ideas and structure of MiniCP and the associated MOOC materials for teaching constraint programming.

## License

MIT License. See `LICENSE`.
