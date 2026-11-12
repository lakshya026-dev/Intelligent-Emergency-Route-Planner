"""
Graph Builder Module – Downloads and processes road networks from OpenStreetMap.

Uses OSMnx to download drivable road networks for a given place name, enriches
edges with travel-time attributes based on speed limits (falling back to
``config.DEFAULT_SPEEDS``), simplifies the topology, and optionally caches the
raw and processed graphs to disk.
"""

import logging
import os
import pickle
from pathlib import Path
from typing import Optional, Any

try:
    import networkx as nx
except ImportError:
    nx = None

try:
    import osmnx as ox
except ImportError:
    ox = None

from config import (
    DEFAULT_SPEEDS,
    GRAPH_CACHE_ENABLED,
    GRAPH_SIMPLIFY,
    NETWORK_TYPE,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    SUPPORTED_CITIES,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────

def _safe_place_slug(place_name: str) -> str:
    """Convert a human-readable place name to a filesystem-safe slug.

    Args:
        place_name: E.g. ``"Dublin, Ireland"``.

    Returns:
        Lower-cased, whitespace-stripped slug such as ``"dublin_ireland"``.
    """
    return place_name.strip().lower().replace(",", "").replace(" ", "_")


def _parse_maxspeed(maxspeed_value) -> Optional[float]:
    """Parse an OSM ``maxspeed`` tag value into km/h.

    Handles plain numeric strings, ``"XX mph"`` annotations, and list values
    (takes the first parseable entry).

    Args:
        maxspeed_value: Raw value from the OSM ``maxspeed`` tag.

    Returns:
        Speed in km/h, or ``None`` if the value cannot be parsed.
    """
    if maxspeed_value is None:
        return None

    # OSM may store lists when multiple values exist
    if isinstance(maxspeed_value, list):
        for item in maxspeed_value:
            parsed = _parse_maxspeed(item)
            if parsed is not None:
                return parsed
        return None

    value_str = str(maxspeed_value).strip()
    if not value_str:
        return None

    # Handle "XX mph" → convert to km/h
    if "mph" in value_str.lower():
        try:
            return float(value_str.lower().replace("mph", "").strip()) * 1.60934
        except ValueError:
            return None

    # Plain numeric
    try:
        return float(value_str)
    except ValueError:
        return None


def _get_speed_kmh(edge_data: dict) -> float:
    """Determine the travel speed in km/h for a single edge.

    Tries the ``maxspeed`` tag first; falls back to ``config.DEFAULT_SPEEDS``
    based on the ``highway`` tag.

    Args:
        edge_data: Edge attribute dictionary from the NetworkX graph.

    Returns:
        Speed in km/h (always ≥ 1).
    """
    # Try maxspeed tag
    speed = _parse_maxspeed(edge_data.get("maxspeed"))
    if speed is not None and speed > 0:
        return speed

    # Fallback to highway-type defaults
    highway = edge_data.get("highway", "default")
    if isinstance(highway, list):
        highway = highway[0]

    return DEFAULT_SPEEDS.get(highway, DEFAULT_SPEEDS["default"])


def _calculate_travel_time(length_m: float, speed_kmh: float) -> float:
    """Calculate traversal time for an edge.

    Args:
        length_m: Edge length in meters.
        speed_kmh: Travel speed in km/h.

    Returns:
        Travel time in seconds.
    """
    speed_mps = speed_kmh / 3.6  # km/h → m/s
    if speed_mps <= 0:
        speed_mps = DEFAULT_SPEEDS["default"] / 3.6
    return length_m / speed_mps


# ──────────────────────────────────────────────
# Cache helpers
# ──────────────────────────────────────────────

def _raw_graphml_path(place_name: str) -> Path:
    """Return the path for the raw GraphML cache file."""
    return RAW_DATA_DIR / f"{_safe_place_slug(place_name)}.graphml"


def _processed_pickle_path(place_name: str) -> Path:
    """Return the path for the processed pickle cache file."""
    return PROCESSED_DATA_DIR / f"{_safe_place_slug(place_name)}.pkl"


def _save_raw_graph(graph: Any, place_name: str) -> None:
    """Save the raw downloaded graph as GraphML."""
    path = _raw_graphml_path(place_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    if ox is not None:
        ox.save_graphml(graph, filepath=path)
        logger.info("Raw graph saved to %s", path)


def _save_processed_graph(graph: Any, place_name: str) -> None:
    """Save the fully processed graph as a pickle."""
    path = _processed_pickle_path(place_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as fh:
        pickle.dump(graph, fh, protocol=pickle.HIGHEST_PROTOCOL)
    logger.info("Processed graph saved to %s", path)


def _load_processed_graph(place_name: str) -> Optional[Any]:
    """Load a processed graph from the pickle cache, if it exists."""
    path = _processed_pickle_path(place_name)
    if path.exists():
        logger.info("Loading processed graph from cache: %s", path)
        with open(path, "rb") as fh:
            return pickle.load(fh)
    return None


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def enrich_graph_attributes(graph: Any) -> Any:
    """Add ``travel_time`` (seconds) to every edge that lacks one.

    Also ensures every edge has a ``length`` attribute (uses OSMnx to add
    edge lengths if missing).

    Args:
        graph: A NetworkX ``MultiDiGraph`` (typically from OSMnx).

    Returns:
        The same graph, mutated in place, with ``travel_time`` on all edges.
    """
    # Ensure lengths exist
    if not all("length" in d for _, _, _, d in graph.edges(keys=True, data=True)):
        graph = ox.distance.add_edge_lengths(graph)

    for u, v, key, data in graph.edges(keys=True, data=True):
        # Preserve OSMnx's full LineString as plain coordinates so it survives
        # processed-graph caching and can be rendered without Shapely objects.
        geometry = data.get("geometry")
        if geometry is not None and hasattr(geometry, "coords"):
            data["geometry_coords"] = [(float(lat), float(lon)) for lon, lat in geometry.coords]
        elif "geometry_coords" not in data:
            data["geometry_coords"] = [
                (float(graph.nodes[u]["y"]), float(graph.nodes[u]["x"])),
                (float(graph.nodes[v]["y"]), float(graph.nodes[v]["x"])),
            ]
        length_m = data.get("length", 0.0)
        speed_kmh = _get_speed_kmh(data)
        data["travel_time"] = _calculate_travel_time(length_m, speed_kmh)
        # Also store resolved speed for downstream consumers
        data["speed_kmh"] = speed_kmh

    return graph


def download_graph(place_name: str,
                   network_type: str = NETWORK_TYPE,
                   simplify: bool = GRAPH_SIMPLIFY,
                   cache: bool = GRAPH_CACHE_ENABLED) -> Any:
    """Download a road-network graph from OpenStreetMap via OSMnx.

    The graph is enriched with ``travel_time`` edge attributes and optionally
    cached to disk (raw GraphML in ``data/raw/``, processed pickle in
    ``data/processed/``).

    Args:
        place_name: Geocodable place name, e.g. ``"Dublin, Ireland"``.
        network_type: OSMnx network type (default from config).
        simplify: Whether to simplify the graph topology.
        cache: Whether to save/load cached copies.

    Returns:
        A processed ``MultiDiGraph`` ready for routing.

    Raises:
        ValueError: If *place_name* is not in ``config.SUPPORTED_CITIES``.
        Exception: Propagates network errors from OSMnx.
    """
    if place_name not in SUPPORTED_CITIES:
        raise ValueError(
            f"Unsupported city: {place_name!r}. "
            f"Supported: {list(SUPPORTED_CITIES)}"
        )

    # ── Check processed cache first ──
    if cache:
        cached = _load_processed_graph(place_name)
        if cached is not None:
            return cached

    if ox is None:
        raise RuntimeError("OSMnx is required to download a road network.")

    logger.info("Downloading road network for '%s' …", place_name)
    download_errors = []
    queries = [place_name]
    if place_name == "Mumbai, India":
        queries = ["Mumbai, Maharashtra, India", place_name]
    for query in queries:
        try:
            graph = ox.graph_from_place(query, network_type=network_type, simplify=simplify)
            break
        except Exception as exc:
            download_errors.append(f"{query}: {exc}")
            logger.warning("OSM place download failed for %s: %s", query, exc)
    else:
        if place_name != "Mumbai, India":
            raise RuntimeError("Could not download road network: " + "; ".join(download_errors))
        # A city geocoder may return a Point instead of a polygon. Download a
        # configurable-radius drive network around the known Mumbai center.
        center = SUPPORTED_CITIES[place_name]["center"]
        radius = int(os.getenv("MUMBAI_GRAPH_RADIUS_METERS", "12000"))
        try:
            graph = ox.graph_from_point(center, dist=radius, network_type=network_type,
                                        simplify=simplify)
        except Exception as exc:
            download_errors.append(f"Mumbai center/radius fallback: {exc}")
            raise RuntimeError(
                f"Could not download the road network for '{place_name}'. "
                "Place lookup and Mumbai center/radius fallback both failed. "
                + "; ".join(download_errors)
            ) from exc

    # Save raw snapshot
    if cache:
        _save_raw_graph(graph, place_name)

    # Enrich with travel-time attributes
    graph = enrich_graph_attributes(graph)

    # Save processed snapshot
    if cache:
        _save_processed_graph(graph, place_name)

    logger.info(
        "Graph ready: %d nodes, %d edges",
        graph.number_of_nodes(),
        graph.number_of_edges(),
    )
    return graph
