"""
Heuristic Functions – Admissible heuristics for informed search algorithms.

All heuristics in this module are *admissible*: they never overestimate the
true cost, which guarantees A* optimality when used with a consistent cost
function.
"""

import math


# Earth's mean radius in metres (WGS-84 derived)
_EARTH_RADIUS_M = 6_371_000.0


def haversine_distance(lat1: float, lon1: float,
                       lat2: float, lon2: float) -> float:
    """Return the great-circle (straight-line) distance in metres.

    Uses the Haversine formula, which is accurate for all distances on a
    spherical Earth model.

    **Admissibility**: The straight-line distance is always ≤ the shortest
    road-network distance, so it never overestimates.

    Args:
        lat1: Latitude of point 1 in decimal degrees.
        lon1: Longitude of point 1 in decimal degrees.
        lat2: Latitude of point 2 in decimal degrees.
        lon2: Longitude of point 2 in decimal degrees.

    Returns:
        Distance in metres (≥ 0).
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2
         + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return _EARTH_RADIUS_M * c


def time_heuristic(lat1: float, lon1: float,
                   lat2: float, lon2: float,
                   max_speed_mps: float = 33.333) -> float:
    """Return a lower-bound travel time in seconds between two points.

    Computed as ``haversine_distance / max_speed_mps``, where *max_speed_mps*
    is the maximum speed (in **metres per second**) achievable on any edge in
    the graph.  Because no vehicle can exceed this speed, the true travel time
    is always ≥ this value, making the heuristic admissible.

    Args:
        lat1: Latitude of point 1 in decimal degrees.
        lon1: Longitude of point 1 in decimal degrees.
        lat2: Latitude of point 2 in decimal degrees.
        lon2: Longitude of point 2 in decimal degrees.
        max_speed_mps: Maximum edge speed in the graph, in metres per second.
            Must be > 0.

    Returns:
        Lower-bound travel time in seconds (≥ 0).

    Raises:
        ValueError: If *max_speed_mps* ≤ 0.
    """
    if max_speed_mps <= 0:
        raise ValueError(
            f"max_speed_mps must be positive, got {max_speed_mps}"
        )

    distance = haversine_distance(lat1, lon1, lat2, lon2)
    return distance / max_speed_mps
