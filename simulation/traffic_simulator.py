"""
Traffic Simulation Engine.

Generates and applies traffic conditions to a road-network graph,
allowing uniform, random, or custom traffic overlays.
"""

import random
import config


class TrafficSimulator:
    """Simulates traffic conditions on a road-network graph."""

    def __init__(self, seed: int = config.TRAFFIC_RANDOM_SEED):
        """
        Initialize the traffic simulator.

        Args:
            seed: Random seed for reproducible traffic generation.
        """
        self.seed = seed
        self._rng = random.Random(seed)


    def generate_traffic(self, graph, condition: str = "Normal"):
        """
        Apply a single traffic condition to every edge in the graph.

        Adds ``traffic_multiplier`` and ``traffic_travel_time`` attributes
        to each edge.  Works on a **copy** — the original graph is never
        modified.

        Args:
            graph: A NetworkX MultiDiGraph with ``travel_time`` edge attrs.
            condition: One of the keys in ``config.TRAFFIC_CONDITIONS``
                       (default ``'Normal'``).

        Returns:
            A modified copy of the graph with traffic attributes set.

        Raises:
            ValueError: If *condition* is not in TRAFFIC_CONDITIONS.
        """
        if condition not in config.TRAFFIC_CONDITIONS:
            raise ValueError(
                f"Unknown traffic condition '{condition}'. "
                f"Valid options: {list(config.TRAFFIC_CONDITIONS.keys())}"
            )

        multiplier = config.TRAFFIC_CONDITIONS[condition]["multiplier"]
        g = graph.copy()

        for u, v, key, data in g.edges(keys=True, data=True):
            base_time = data.get("travel_time", 0)
            g[u][v][key]["traffic_multiplier"] = multiplier
            g[u][v][key]["traffic_condition"] = condition
            g[u][v][key]["traffic_travel_time"] = base_time * multiplier

        return g

    def apply_traffic(self, graph, condition: str = "Normal"):
        """Alias for generate_traffic."""
        return self.generate_traffic(graph, condition)




    # ------------------------------------------------------------------ #
    #  Random traffic
    # ------------------------------------------------------------------ #
    def generate_random_traffic(self, graph, seed=None):
        """
        Assign a random traffic condition to each edge independently.

        Uses *seed* (or the instance seed) for reproducibility.

        Args:
            graph: A NetworkX MultiDiGraph with ``travel_time`` edge attrs.
            seed: Optional override seed for the random generator.

        Returns:
            A modified copy of the graph with per-edge traffic attributes.
        """
        rng = random.Random(seed if seed is not None else self.seed)
        conditions = list(config.TRAFFIC_CONDITIONS.keys())

        g = graph.copy()

        for u, v, key, data in g.edges(keys=True, data=True):
            cond = rng.choice(conditions)
            multiplier = config.TRAFFIC_CONDITIONS[cond]["multiplier"]
            base_time = data.get("travel_time", 0)
            g[u][v][key]["traffic_multiplier"] = multiplier
            g[u][v][key]["traffic_condition"] = cond
            g[u][v][key]["traffic_travel_time"] = base_time * multiplier

        return g

    def apply_traffic(self, graph, condition: str = "Normal"):
        """Alias for generate_traffic."""
        return self.generate_traffic(graph, condition)




    # ------------------------------------------------------------------ #
    #  Distribution query
    # ------------------------------------------------------------------ #
    @staticmethod
    def get_traffic_distribution(graph) -> dict:
        """
        Count the number of edges at each traffic level.

        Args:
            graph: A graph whose edges have a ``traffic_condition`` attribute.

        Returns:
            A dict mapping each traffic-condition name to its edge count.
        """
        distribution: dict[str, int] = {
            cond: 0 for cond in config.TRAFFIC_CONDITIONS
        }

        for _u, _v, _key, data in graph.edges(keys=True, data=True):
            cond = data.get("traffic_condition")
            if cond in distribution:
                distribution[cond] += 1

        return distribution

    # ------------------------------------------------------------------ #
    #  Custom traffic data
    # ------------------------------------------------------------------ #
    @staticmethod
    def apply_traffic_to_graph(graph, traffic_data: dict):
        """
        Apply caller-supplied traffic data to specific edges.

        Args:
            graph: A NetworkX MultiDiGraph.
            traffic_data: A dict keyed by ``(u, v, key)`` tuples, where
                each value is a dict with at least ``'condition'`` (str)
                or ``'multiplier'`` (float).

        Returns:
            A modified copy of the graph.
        """
        g = graph.copy()

        for (u, v, key), info in traffic_data.items():
            if g.has_edge(u, v, key=key):
                edge = g[u][v][key]
                base_time = edge.get("travel_time", 0)

                if "condition" in info:
                    cond = info["condition"]
                    multiplier = config.TRAFFIC_CONDITIONS.get(
                        cond, {}
                    ).get("multiplier", 1.0)
                    edge["traffic_condition"] = cond
                elif "multiplier" in info:
                    multiplier = info["multiplier"]
                    edge["traffic_condition"] = "Custom"
                else:
                    multiplier = 1.0
                    edge["traffic_condition"] = "Normal"

                edge["traffic_multiplier"] = multiplier
                edge["traffic_travel_time"] = base_time * multiplier

        return g

    def apply_traffic(self, graph, condition: str = "Normal"):
        """Alias for generate_traffic."""
        return self.generate_traffic(graph, condition)



