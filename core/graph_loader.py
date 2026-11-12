"""
Graph Loader Module – High-level entry point for obtaining a road-network graph.

Loads a cached processed graph from ``data/processed/`` when available;
otherwise delegates to :func:`core.graph_builder.download_graph`. When the
network is unreachable, a useful download error is raised.
"""

import logging
import math
import random
from typing import Optional, Any

try:
    import networkx as nx
    MultiDiGraph = nx.MultiDiGraph
except ImportError:
    nx = None
    from core.simple_graph import SimpleMultiDiGraph as MultiDiGraph

from config import (
    DEFAULT_CITY,
    DEFAULT_SPEEDS,
    GRAPH_CACHE_ENABLED,
    PROCESSED_DATA_DIR,
    SUPPORTED_CITIES,
)
from core.graph_builder import (
    _processed_pickle_path,
    _load_processed_graph,
    download_graph,
    enrich_graph_attributes,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def load_graph(place_name: str = DEFAULT_CITY,
               cache: bool = GRAPH_CACHE_ENABLED) -> Any:
    """Load (or download) the road-network graph for *place_name*.

    Resolution order: processed pickle cache, then a fresh OSM download.

    Args:
        place_name: A city name that appears in ``config.SUPPORTED_CITIES``.
        cache: Whether to use / update the on-disk cache.

    Returns:
        A ``MultiDiGraph`` ready for routing algorithms.
    """
    # 1. Try cached processed graph
    if cache:
        cached = _load_processed_graph(place_name)
        if cached is not None:
            logger.info("Loaded cached graph for '%s'.", place_name)
            return cached

    # 2. Try downloading
    try:
        graph = download_graph(place_name, cache=cache)
        return graph
    except Exception as exc:
        logger.warning("Failed to download graph for '%s': %s", place_name, exc)

    raise RuntimeError(
        f"Could not load the real OpenStreetMap road network for '{place_name}'. "
        "Check your internet connection or OSM/Nominatim availability, then retry."
    )


# ──────────────────────────────────────────────
# Fallback synthetic graph
# ──────────────────────────────────────────────

def create_fallback_graph(
    city_name: Any = DEFAULT_CITY,
    num_nodes: int = 80,
    seed: int = 42,
) -> Any:
    """Build a synthetic road network centered on the requested city.

    The graph is a valid MultiDiGraph whose structure mirrors what OSMnx produces:
    nodes carry ``x`` (longitude) and ``y`` (latitude) attributes with accurate
    geographical coordinates corresponding to the chosen city, and edges carry
    ``length`` (m), ``highway``, ``maxspeed``, ``travel_time`` (s), and ``speed_kmh``.

    Args:
        city_name: City name from ``config.SUPPORTED_CITIES`` (or int for backwards compatibility).
        num_nodes: Minimum number of nodes to generate (actual count >= this).
        seed: Random seed for reproducibility.

    Returns:
        A ``MultiDiGraph`` compatible with OSMnx-produced graphs.
    """
    if isinstance(city_name, int):
        num_nodes = city_name
        city_name = DEFAULT_CITY

    rng = random.Random(seed)

    city_info = SUPPORTED_CITIES.get(city_name)
    if city_info is not None:
        CENTER_LAT, CENTER_LON = city_info["center"]
    else:
        CENTER_LAT, CENTER_LON = 53.3498, -6.2603

    # Approximate degree offsets for ~100 m adjusted by latitude cos factor
    DEG_PER_100M_LAT = 0.0009
    cos_lat = max(0.2, math.cos(math.radians(CENTER_LAT)))
    DEG_PER_100M_LON = 0.0009 / cos_lat

    # Lay nodes on a grid
    grid_side = math.ceil(math.sqrt(num_nodes))
    spacing = 3  # units of 100 m

    G = MultiDiGraph(crs="EPSG:4326", name=f"{city_name} Network Graph")

    node_id = 0
    node_grid = {}  # (row, col) → node_id

    for row in range(grid_side):
        for col in range(grid_side):
            lat = CENTER_LAT + (row - grid_side // 2) * spacing * DEG_PER_100M_LAT
            lon = CENTER_LON + (col - grid_side // 2) * spacing * DEG_PER_100M_LON

            # Small jitter for realism
            lat += rng.uniform(-0.0002, 0.0002)
            lon += rng.uniform(-0.0003, 0.0003)

            G.add_node(node_id, y=lat, x=lon, street_count=0)
            node_grid[(row, col)] = node_id
            node_id += 1

    # Road-type assignments based on position
    highway_types = ["primary", "secondary", "tertiary", "residential"]

    def _haversine(lat1, lon1, lat2, lon2):
        """Return distance in metres between two lat/lon pairs."""
        R = 6_371_000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _add_edge(u, v, highway):
        data_u = G.nodes[u]
        data_v = G.nodes[v]
        length = _haversine(data_u["y"], data_u["x"], data_v["y"], data_v["x"])
        speed_kmh = DEFAULT_SPEEDS.get(highway, DEFAULT_SPEEDS["default"])
        travel_time = length / (speed_kmh / 3.6) if speed_kmh > 0 else length / (40 / 3.6)
        G.add_edge(
            u, v, key=0,
            length=length,
            highway=highway,
            maxspeed=str(speed_kmh),
            travel_time=travel_time,
            speed_kmh=speed_kmh,
            oneway=False,
            name=f"Fallback Road {u}-{v}",
        )

    # Connect grid neighbours (horizontal + vertical) ⇒ bidirectional
    for row in range(grid_side):
        for col in range(grid_side):
            current = node_grid[(row, col)]

            # Determine road type: main axes are primary, rest varies
            if row == grid_side // 2 or col == grid_side // 2:
                hw = "primary"
            elif row % 3 == 0 or col % 3 == 0:
                hw = "secondary"
            else:
                hw = rng.choice(["tertiary", "residential"])

            # Right neighbour
            if col + 1 < grid_side:
                neighbour = node_grid[(row, col + 1)]
                _add_edge(current, neighbour, hw)
                _add_edge(neighbour, current, hw)

            # Down neighbour
            if row + 1 < grid_side:
                neighbour = node_grid[(row + 1, col)]
                _add_edge(current, neighbour, hw)
                _add_edge(neighbour, current, hw)

    # Add a handful of diagonal shortcuts for variety
    diag_count = max(5, grid_side)
    for _ in range(diag_count):
        r1 = rng.randint(0, grid_side - 2)
        c1 = rng.randint(0, grid_side - 2)
        r2 = r1 + 1
        c2 = c1 + 1
        u, v = node_grid[(r1, c1)], node_grid[(r2, c2)]
        if not G.has_edge(u, v):
            _add_edge(u, v, "tertiary")
            _add_edge(v, u, "tertiary")

    # Update street_count for each node (number of incident edges)
    for n in G.nodes:
        G.nodes[n]["street_count"] = G.degree(n)

    logger.info(
        "Fallback graph created: %d nodes, %d edges",
        G.number_of_nodes(),
        G.number_of_edges(),
    )
    return G
