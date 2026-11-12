"""
Breadth-First Search (BFS) algorithm for emergency route planning.

BFS explores the graph level by level using a FIFO queue, guaranteeing the
shortest path in terms of number of hops (edges).  It does NOT consider edge
weights when choosing which node to explore next.
"""

import time
from collections import deque

from algorithms.algorithm_utils import (
    AlgorithmResult,
    calculate_path_metrics,
    reconstruct_path,
)


def bfs_search(graph, start, goal, weight_attr='length'):
    """Run Breadth-First Search on *graph* from *start* to *goal*.

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
        (default ``'length'``).  BFS itself ignores edge weights.

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
            algorithm_name='BFS',
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
            algorithm_name='BFS',
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
            algorithm_name='BFS',
        )

    # --- BFS core ---
    visited = {start}
    parent_map = {}
    queue = deque([start])
    nodes_explored = 0
    edges_traversed = 0

    while queue:
        current = queue.popleft()
        nodes_explored += 1

        for neighbor in graph.neighbors(current):
            edges_traversed += 1

            if neighbor in visited:
                continue

            visited.add(neighbor)
            parent_map[neighbor] = current

            if neighbor == goal:
                # Reconstruct path & compute metrics
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
                    algorithm_name='BFS',
                )

            queue.append(neighbor)

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
        algorithm_name='BFS',
    )
