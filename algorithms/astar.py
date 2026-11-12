"""
A* Search algorithm for emergency route planning.

A* combines the actual cost from the start (g) with an admissible heuristic
estimate to the goal (h), expanding the node with the lowest f = g + h.
It guarantees an optimal path when the heuristic is admissible and consistent.
"""

import heapq
import time

from algorithms.algorithm_utils import (
    AlgorithmResult,
    calculate_path_metrics,
    reconstruct_path,
)
from core.cost_calculator import get_edge_cost
from core.heuristic import haversine_distance, time_heuristic


def astar_search(graph, start, goal, weight_attr='length'):
    """Run A* Search on *graph* from *start* to *goal*.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        Road-network graph with node/edge attributes.
    start : int
        OSM node ID of the origin.
    goal : int
        OSM node ID of the destination.
    weight_attr : str, optional
        Edge attribute used for g-cost calculation (default ``'length'``).
        When set to a time-based attribute (e.g. ``'travel_time'`` or
        ``'traffic_travel_time'``), the heuristic switches to
        ``time_heuristic`` so that it remains admissible.

    Returns
    -------
    AlgorithmResult
        Dataclass containing the path, metrics, and search statistics.
    """
    start_time = time.perf_counter()

    # --- Edge-case: start equals goal ---
    if start == goal:
        execution_time = time.perf_counter() - start_time
        return AlgorithmResult(
            found=True,
            path=[start],
            total_distance=0.0,
            total_travel_time=0.0,
            nodes_explored=1,
            edges_traversed=0,
            execution_time=execution_time,
            algorithm_name='A*',
        )

    # --- Validate nodes exist in graph ---
    if start not in graph.nodes:
        execution_time = time.perf_counter() - start_time
        return AlgorithmResult(
            found=False,
            path=[],
            total_distance=0.0,
            total_travel_time=0.0,
            nodes_explored=0,
            edges_traversed=0,
            execution_time=execution_time,
            algorithm_name='A*',
        )

    if goal not in graph.nodes:
        execution_time = time.perf_counter() - start_time
        return AlgorithmResult(
            found=False,
            path=[],
            total_distance=0.0,
            total_travel_time=0.0,
            nodes_explored=0,
            edges_traversed=0,
            execution_time=execution_time,
            algorithm_name='A*',
        )

    # --- Choose heuristic based on weight_attr ---
    # For time-based optimisation the heuristic must return a lower-bound
    # travel time; for distance-based it returns haversine distance.
    use_time_heuristic = weight_attr in ('travel_time', 'traffic_travel_time')

    goal_lat = graph.nodes[goal]['y']
    goal_lon = graph.nodes[goal]['x']

    def _heuristic(node):
        """Return admissible heuristic estimate from *node* to *goal*."""
        n_lat = graph.nodes[node]['y']
        n_lon = graph.nodes[node]['x']
        if use_time_heuristic:
            return time_heuristic(n_lat, n_lon, goal_lat, goal_lon)
        return haversine_distance(n_lat, n_lon, goal_lat, goal_lon)

    # --- A* core ---
    g_costs = {start: 0.0}
    parent_map = {}
    visited = set()
    counter = 0  # tie-breaker for deterministic heap ordering
    nodes_explored = 0
    edges_traversed = 0

    h_start = _heuristic(start)
    open_heap = [(h_start, counter, start)]  # (f_cost, counter, node)

    while open_heap:
        f_cost, _cnt, current = heapq.heappop(open_heap)

        if current in visited:
            continue

        visited.add(current)
        nodes_explored += 1

        if current == goal:
            path = reconstruct_path(parent_map, start, goal)
            total_distance, total_travel_time = calculate_path_metrics(
                graph, path, weight_attr,
            )
            execution_time = time.perf_counter() - start_time
            return AlgorithmResult(
                found=True,
                path=path,
                total_distance=total_distance,
                total_travel_time=total_travel_time,
                nodes_explored=nodes_explored,
                edges_traversed=edges_traversed,
                execution_time=execution_time,
                algorithm_name='A*',
            )

        current_g = g_costs[current]

        for neighbor in graph.neighbors(current):
            edges_traversed += 1

            if neighbor in visited:
                continue

            # Use key=0 for the first parallel edge (MultiDiGraph)
            edge_cost = get_edge_cost(graph, current, neighbor, key=0,
                                      weight_attr=weight_attr)
            tentative_g = current_g + edge_cost

            if tentative_g < g_costs.get(neighbor, float('inf')):
                g_costs[neighbor] = tentative_g
                parent_map[neighbor] = current
                f = tentative_g + _heuristic(neighbor)
                counter += 1
                heapq.heappush(open_heap, (f, counter, neighbor))

    # --- Goal unreachable ---
    execution_time = time.perf_counter() - start_time
    return AlgorithmResult(
        found=False,
        path=[],
        total_distance=0.0,
        total_travel_time=0.0,
        nodes_explored=nodes_explored,
        edges_traversed=edges_traversed,
        execution_time=execution_time,
        algorithm_name='A*',
    )
