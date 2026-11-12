"""
Algorithm Utilities – Shared helpers for all routing algorithms.

Contains the canonical ``AlgorithmResult`` data class, path reconstruction
from parent-pointer maps, and path-metric computation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

try:
    import networkx as nx
except ImportError:
    nx = None


# ──────────────────────────────────────────────
# Result data class
# ──────────────────────────────────────────────

@dataclass
class AlgorithmResult:
    """Container for the output of any routing algorithm.

    Attributes:
        found: ``True`` if a path from start to goal was discovered.
        path: Ordered list of node IDs from start to goal (empty when
            *found* is ``False``).
        total_distance: Sum of ``length`` attributes along the path, in
            metres.
        total_travel_time: Sum of ``travel_time`` attributes along the path,
            in seconds.
        nodes_explored: Number of unique nodes removed from the frontier
            (expanded / visited).
        edges_traversed: Number of edges examined during the search.
        execution_time: Wall-clock time of the algorithm run, in seconds.
        algorithm_name: Human-readable name of the algorithm that produced
            this result (e.g. ``"A*"``, ``"BFS"``).
    """

    found: bool = False
    path: List[int] = field(default_factory=list)
    total_distance: float = 0.0
    total_travel_time: float = 0.0
    nodes_explored: int = 0
    edges_traversed: int = 0
    execution_time: float = 0.0
    algorithm_name: str = ""


# ──────────────────────────────────────────────
# Path reconstruction
# ──────────────────────────────────────────────

def reconstruct_path(parent_map: Dict[int, int],
                     start: int,
                     goal: int) -> List[int]:
    """Build an ordered node-ID list from parent pointers.

    Traces back from *goal* to *start* using *parent_map* and returns the
    path in forward order ``[start, …, goal]``.

    Args:
        parent_map: Mapping ``{child_node: parent_node}`` produced during
            graph search.  ``start`` should map to ``None`` (or simply not
            appear as a value).
        start: Source node ID.
        goal: Destination node ID.

    Returns:
        List of node IDs from *start* to *goal* (inclusive), or an empty
        list if *goal* is unreachable (not present in *parent_map* and not
        equal to *start*).
    """
    if goal == start:
        return [start]

    path: List[int] = []
    current: Optional[int] = goal

    while current is not None:
        path.append(current)
        if current == start:
            break
        current = parent_map.get(current)
    else:
        # goal was never connected back to start
        return []

    path.reverse()

    # Sanity check
    if path[0] != start:
        return []

    return path


# ──────────────────────────────────────────────
# Path metrics
# ──────────────────────────────────────────────

def calculate_path_metrics(
    graph: Any,
    path: List[int],
    weight_attr: str = "travel_time",
) -> tuple:
    """Compute total distance (m) and total travel time (s) for a path.

    Iterates over consecutive node pairs in *path*, summing ``length`` and
    *weight_attr* on the shortest (by *weight_attr*) parallel edge.

    Args:
        graph: The road-network ``MultiDiGraph``.
        path: Ordered list of node IDs.
        weight_attr: Edge attribute used as the time/cost metric
            (default ``"travel_time"``).

    Returns:
        ``(total_distance, total_travel_time)`` — distance in metres,
        travel time in seconds.  Both are ``0.0`` for an empty or
        single-node path.
    """
    if len(path) < 2:
        return 0.0, 0.0

    total_distance = 0.0
    total_travel_time = 0.0

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]

        # Select the best parallel edge by weight_attr
        edge_data_dict = graph.get_edge_data(u, v)
        if edge_data_dict is None:
            # Edge missing – should not happen on a valid path
            continue

        # Pick edge with lowest cost
        best_data = min(
            edge_data_dict.values(),
            key=lambda d: d.get(weight_attr, d.get("length", float("inf"))),
        )

        total_distance += best_data.get("length", 0.0)
        total_travel_time += best_data.get(weight_attr, best_data.get("length", 0.0))

    return total_distance, total_travel_time
