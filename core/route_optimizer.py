"""
Central route optimization service.

Coordinates graph preparation (traffic, closures, emergency priority)
and algorithm execution for emergency route planning.
"""

import math
import time

from algorithms.bfs import bfs_search
from algorithms.dfs import dfs_search
from algorithms.greedy import greedy_search
from algorithms.astar import astar_search


# Map user-facing algorithm names to their search functions
_ALGORITHM_MAP = {
    "BFS": bfs_search,
    "DFS": dfs_search,
    "Greedy": greedy_search,
    "A*": astar_search,
}


class RouteOptimizer:
    """Orchestrates graph preparation and route-finding across algorithms."""

    def __init__(self, graph):
        """
        Initialize with the original road-network graph.

        Args:
            graph: A NetworkX MultiDiGraph (OSMnx-style). Never modified.
        """
        self._original_graph = graph

    # ------------------------------------------------------------------ #
    # Graph preparation
    # ------------------------------------------------------------------ #
    def prepare_graph(
        self,
        traffic_condition="Normal",
        vehicle_type="Ambulance",
        closed_roads=None,
        traffic_simulator=None,
        road_closure_manager=None,
        emergency_manager=None,
    ):
        """
        Create a working copy of the graph with simulated conditions applied.

        Applies, in order:
            1. Traffic simulation  (via *traffic_simulator*)
            2. Road closures       (via *road_closure_manager*)
            3. Emergency priority  (via *emergency_manager*)

        Args:
            traffic_condition: Key into config.TRAFFIC_CONDITIONS (e.g. 'Heavy').
            vehicle_type: Key into config.EMERGENCY_VEHICLES (e.g. 'Ambulance').
            closed_roads: List of (u, v) or (u, v, key) tuples to close.
            traffic_simulator: A TrafficSimulator instance (or None to skip).
            road_closure_manager: A RoadClosureManager instance (or None to skip).
            emergency_manager: An EmergencyPriorityManager instance (or None to skip).

        Returns:
            A modified *copy* of the graph with all conditions applied.
        """
        prepared = self._original_graph.copy()

        # 1. Traffic simulation
        if traffic_simulator is not None:
            prepared = traffic_simulator.apply_traffic(prepared, traffic_condition)

        # 2. Road closures
        if road_closure_manager is not None:
            if closed_roads:
                for road in closed_roads:
                    if len(road) == 2:
                        road_closure_manager.close_road(road[0], road[1])
                    else:
                        road_closure_manager.close_road(road[0], road[1], road[2])
            prepared = road_closure_manager.apply_closures(prepared)

        # 3. Emergency priority
        if emergency_manager is not None:
            prepared = emergency_manager.apply_priority(prepared, vehicle_type)

        return prepared

    # ------------------------------------------------------------------ #
    # Route finding
    # ------------------------------------------------------------------ #
    def find_route(
        self,
        prepared_graph,
        start,
        goal,
        algorithm="A*",
        weight_attr="length",
    ):
        """
        Run a single search algorithm on the prepared graph.

        Args:
            prepared_graph: Graph returned by :meth:`prepare_graph`.
            start: Source node ID.
            goal: Destination node ID.
            algorithm: One of 'BFS', 'DFS', 'Greedy', 'A*'.
            weight_attr: Edge attribute used as cost (e.g. 'length', 'travel_time').

        Returns:
            An AlgorithmResult dataclass with search results.

        Raises:
            ValueError: If the algorithm name is not recognized.
        """
        search_fn = _ALGORITHM_MAP.get(algorithm)
        if search_fn is None:
            raise ValueError(
                f"Unknown algorithm '{algorithm}'. "
                f"Choose from {list(_ALGORITHM_MAP.keys())}."
            )
        return search_fn(prepared_graph, start, goal, weight_attr=weight_attr)

    # ------------------------------------------------------------------ #
    # Algorithm comparison
    # ------------------------------------------------------------------ #
    def compare_algorithms(
        self,
        prepared_graph,
        start,
        goal,
        weight_attr="length",
        algorithms=None,
    ):
        """
        Run multiple algorithms on the *same* prepared graph.

        Args:
            prepared_graph: Graph returned by :meth:`prepare_graph`.
            start: Source node ID.
            goal: Destination node ID.
            weight_attr: Edge attribute used as cost.
            algorithms: List of algorithm names to run.
                        Defaults to all four: BFS, DFS, Greedy, A*.

        Returns:
            dict[str, AlgorithmResult]: Mapping algorithm name → result.
        """
        if algorithms is None:
            algorithms = list(_ALGORITHM_MAP.keys())

        results = {}
        for algo_name in algorithms:
            results[algo_name] = self.find_route(
                prepared_graph, start, goal, algorithm=algo_name, weight_attr=weight_attr
            )
        return results

    # ------------------------------------------------------------------ #
    # Nearest node
    # ------------------------------------------------------------------ #
    @staticmethod
    def get_nearest_node(graph, lat, lon):
        """
        Find the graph node closest to the given (lat, lon) using Euclidean
        distance on the raw coordinate values.

        Args:
            graph: NetworkX graph with 'x' (lon) and 'y' (lat) node attributes.
            lat: Latitude of the query point.
            lon: Longitude of the query point.

        Returns:
            The node ID of the nearest node.
        """
        best_node = None
        best_dist = float("inf")
        for node, data in graph.nodes(data=True):
            node_lat = data.get("y", 0.0)
            node_lon = data.get("x", 0.0)
            dist = math.sqrt((node_lat - lat) ** 2 + (node_lon - lon) ** 2)
            if dist < best_dist:
                best_dist = dist
                best_node = node
        return best_node
