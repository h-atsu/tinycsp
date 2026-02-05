# %%

import itertools
from dataclasses import dataclass

import geopandas as gpd
import matplotlib.pyplot as plt
from tinycsp import TinyCSP

# %%
# --- Data source (prefecture polygons) ---
# geolonia/prefecture-tiles provides prefectures.geojson
GEOJSON_URL = "https://raw.githubusercontent.com/geolonia/prefecture-tiles/master/prefectures.geojson"


@dataclass(frozen=True)
class ColoringResult:
    color_of: dict[str, int]  # prefecture name -> color (0..k-1)
    num_colors: int
    edges: list[tuple[str, str]]  # adjacency list (undirected)


def load_prefectures() -> gpd.GeoDataFrame:
    gdf = gpd.read_file(GEOJSON_URL)

    # Common fields in this dataset: "name" (ja), sometimes "pref" etc.
    # We'll try to pick a reasonable name column.
    name_col = None
    for c in ["name", "pref", "prefecture", "NAME", "nam"]:
        if c in gdf.columns:
            name_col = c
            break
    if name_col is None:
        raise ValueError(
            f"Could not find a prefecture-name column. Columns={list(gdf.columns)}"
        )

    gdf = gdf[[name_col, "geometry"]].rename(columns={name_col: "pref"})
    gdf["pref"] = gdf["pref"].astype(str)

    # Ensure geometries are valid (occasionally needed for touches/intersects)
    gdf["geometry"] = gdf["geometry"].buffer(0)

    # Use a projected CRS for more robust boundary tests (meters)
    # If source is EPSG:4326, convert to EPSG:3857 for topology ops.
    if gdf.crs is None:
        # Many GitHub geojsons omit CRS; assume WGS84
        gdf = gdf.set_crs(4326)
    gdf = gdf.to_crs(3857)

    return gdf


def build_adjacency(gdf: gpd.GeoDataFrame) -> list[tuple[str, str]]:
    """
    Build adjacency edges where prefecture polygons share a boundary segment.
    We use touches() but exclude "point-touch only" using boundary intersection length.
    """
    prefs = gdf["pref"].tolist()
    geoms = gdf["geometry"].tolist()

    edges: list[tuple[str, str]] = []

    def bounds_intersects(a, b) -> bool:
        minx1, miny1, maxx1, maxy1 = a.bounds
        minx2, miny2, maxx2, maxy2 = b.bounds
        return not (maxx1 < minx2 or maxx2 < minx1 or maxy1 < miny2 or maxy2 < miny1)

    for i, j in itertools.combinations(range(len(prefs)), 2):
        a, b = geoms[i], geoms[j]

        # quick reject
        if not bounds_intersects(a, b):
            continue

        # touches means boundaries meet (could be just a point).
        if not a.touches(b):
            continue

        inter = a.boundary.intersection(b.boundary)
        # Accept only if they share a boundary of non-trivial length
        # (avoid "just a point" contact)
        if getattr(inter, "length", 0.0) > 1.0:  # 1 meter threshold
            u, v = prefs[i], prefs[j]
            if u != v:
                edges.append((u, v))

    # normalize
    edges = [(min(u, v), max(u, v)) for (u, v) in edges]
    edges = sorted(set(edges))
    return edges


def solve_min_graph_coloring(
    prefs: list[str], edges: list[tuple[str, str]], max_colors: int = 4
) -> ColoringResult:
    """
    TinyCSP: find a coloring using num clors.
    """
    n = len(prefs)
    idx = {p: i for i, p in enumerate(prefs)}

    csp = TinyCSP()
    vars = [csp.make_variable(max_colors) for _ in range(n)]

    for u, v in edges:
        csp.not_equal(vars[idx[u]], vars[idx[v]])

    # symmetry breaking: fix first node color = 0
    csp.equal(vars[0], 0)

    solutions = []

    csp.dfs(on_solution=lambda sol: solutions.append(sol), stop_after_first=True)

    if len(solutions) == 0:
        raise ValueError(f"No coloring found with {max_colors} colors.")

    solution = solutions[0]

    result = ColoringResult(
        color_of={prefs[i]: solution[i] for i in range(n)},
        num_colors=max_colors,
        edges=edges,
    )

    return result


def _build_palette(num_colors: int) -> list[str]:
    # Base palette matches the reference image (high contrast).
    base = ["#ff0000", "#ffff00", "#0000ff", "#008000"]  # red, yellow, blue, green
    if num_colors <= len(base):
        return base[:num_colors]

    # Extend with a distinct categorical palette to avoid index errors.
    from matplotlib import colors as mcolors

    cmap = plt.get_cmap("tab20")
    extra = [mcolors.to_hex(cmap(i % cmap.N)) for i in range(num_colors - len(base))]
    return base + extra


def plot_coloring(gdf: gpd.GeoDataFrame, res: ColoringResult) -> None:
    # Use japanmap for a simpler prefecture map rendering.
    from japanmap import picture

    palette = _build_palette(res.num_colors)
    color_map = {pref: palette[idx] for pref, idx in res.color_of.items()}

    img = picture(color_map)  # numpy.ndarray
    plt.imshow(img)
    plt.axis("off")
    plt.title(f"Japan Prefectures Graph Coloring (k={res.num_colors})")
    plt.show()


# %%
gdf = load_prefectures()
edges = build_adjacency(gdf)
prefs = sorted(gdf["pref"].tolist())

res = solve_min_graph_coloring(prefs, edges, max_colors=4)

print(f"Number of colors: {res.num_colors}")

plot_coloring(gdf, res)
# %%
