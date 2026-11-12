"""
Greedy Best-First Search algorithm for emergency route planning.

Greedy Best-First Search uses a priority queue ordered solely by the
heuristic estimate h(n) — the straight-line (haversine) distance from the
current node to the goal.  It does NOT guarantee the optimal path but tends
to explore far fewer nodes than BFS/DFS on spatial graphs.
"""

import heapq
import time

from algorithms.algorithm_utils import (
    AlgorithmResult,
    calculate_path_metrics,
    reconstruct_path,
)
from core.heuristic import haversine_distance


def greedy_search(graph, start, goal, weight_attr='length'):
    """Run Greedy Best-First Search on *graph* from *start* to *goal*.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        Road-network graph with node/edge attributes.
    start : int
        OSM node ID of the origin.
    goal : int
        OSM node ID of the destination.
    weight_attr : str, optional
        Edge attribute used when computing path metrics after the search
        (default ``'length'``).  The search ordering itself uses only the
        heuristic.

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
            algorithm_name='Greedy',
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
            algorithm_name='Greedy',
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
            algorithm_name='Greedy',
        )

    # Goal coordinates (used for every heuristic call)
    goal_lat = graph.nodes[goal]['y']
    goal_lon = graph.nodes[goal]['x']

    # --- Greedy core ---
    visited = set()
    parent_map = {}
    counter = 0  # tie-breaker for deterministic ordering
    nodes_explored = 0
    edges_traversed = 0

    start_h = haversine_distance(
        graph.nodes[start]['y'], graph.nodes[start]['x'],
        goal_lat, goal_lon,
    )
    open_heap = [(start_h, counter, start)]

    while open_heap:
        _h, _cnt, current = heapq.heappop(open_heap)

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
                algorithm_name='Greedy',
            )

        for neighbor in graph.neighbors(current):
            edges_traversed += 1

            if neighbor in visited:
                continue

            # Record parent (first discovery wins)
            if neighbor not in parent_map:
                parent_map[neighbor] = current

            h = haversine_distance(
                graph.nodes[neighbor]['y'], graph.nodes[neighbor]['x'],
                goal_lat, goal_lon,
            )
            counter += 1
            heapq.heappush(open_heap, (h, counter, neighbor))

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
        algorithm_name='Greedy',
    )
