"""
Cost Calculator Module – Edge-cost retrieval and travel-time calculations.

Provides simple, reusable functions used by all routing algorithms to
determine the cost of traversing an edge and to convert between physical
quantities.
"""

from typing import Optional, Any

try:
    import networkx as nx
except ImportError:
    nx = None


def get_edge_cost(graph: Any,
                  u: int, v: int, key: int = 0,
                  weight_attr: str = "travel_time") -> float:
    """Retrieve the cost of traversing edge ``(u, v, key)`` in *graph*.

    If the requested *weight_attr* is missing from the edge data the function
    falls back to ``"length"``; if that is also absent it returns ``float('inf')``
    so the edge is effectively avoided by shortest-path searches.

    Args:
        graph: The road-network ``MultiDiGraph``.
        u: Source node ID.
        v: Target node ID.
        key: Edge key (multi-graph parallel-edge index, default ``0``).
        weight_attr: Name of the edge attribute to use as cost
            (e.g. ``"travel_time"``, ``"length"``, ``"traffic_travel_time"``).

    Returns:
        The numeric edge cost (≥ 0), or ``float('inf')`` when unavailable.
    """
    edge_data = graph.get_edge_data(u, v, key)
    if edge_data is None:
        return float("inf")

    cost = edge_data.get(weight_attr)
    if cost is not None:
        return float(cost)

    # Fallback to length
    length = edge_data.get("length")
    if length is not None:
        return float(length)

    return float("inf")


def calculate_travel_time(length_m: float, speed_kmh: float) -> float:
    """Convert distance and speed to travel time.

    Args:
        length_m: Distance in metres (≥ 0).
        speed_kmh: Speed in kilometres per hour (must be > 0).

    Returns:
        Travel time in seconds.

    Raises:
        ValueError: If *speed_kmh* ≤ 0.
    """
    if speed_kmh <= 0:
        raise ValueError(f"speed_kmh must be positive, got {speed_kmh}")
    speed_mps = speed_kmh / 3.6
    return length_m / speed_mps


def apply_traffic_multiplier(base_time: float,
                             multiplier: float = 1.0) -> float:
    """Scale a base travel time by a traffic-condition multiplier.

    A *multiplier* of ``1.0`` means free-flowing traffic; higher values
    represent increasing congestion (see ``config.TRAFFIC_CONDITIONS``).

    Args:
        base_time: Base travel time in seconds (≥ 0).
        multiplier: Traffic multiplier (≥ 1.0 in normal use, but any
            positive value is accepted).

    Returns:
        Adjusted travel time in seconds.

    Raises:
        ValueError: If *multiplier* ≤ 0.
    """
    if multiplier <= 0:
        raise ValueError(f"multiplier must be positive, got {multiplier}")
    return base_time * multiplier
