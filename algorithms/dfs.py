"""
Depth-First Search (DFS) algorithm for emergency route planning.

DFS explores the graph using a LIFO stack, diving as deep as possible along
each branch before backtracking.  It does NOT guarantee the shortest path.
"""

import time

from algorithms.algorithm_utils import (
    AlgorithmResult,
    calculate_path_metrics,
    reconstruct_path,
)


def dfs_search(graph, start, goal, weight_attr='length'):
    """Run Depth-First Search on *graph* from *start* to *goal*.

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
        (default ``'length'``).  DFS itself ignores edge weights.

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
            algorithm_name='DFS',
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
            algorithm_name='DFS',
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
            algorithm_name='DFS',
        )

    # --- DFS core (iterative, using a list as a stack) ---
    visited = set()
    parent_map = {}
    stack = [start]
    nodes_explored = 0
    edges_traversed = 0

    while stack:
        current = stack.pop()

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
                algorithm_name='DFS',
            )

        for neighbor in graph.neighbors(current):
            edges_traversed += 1

            if neighbor not in visited:
                # Only set parent if we haven't already recorded one —
                # the first parent recorded will be the one on the actual
                # DFS path since we check `visited` before expanding.
                if neighbor not in parent_map:
                    parent_map[neighbor] = current
                stack.append(neighbor)

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
        algorithm_name='DFS',
    )
