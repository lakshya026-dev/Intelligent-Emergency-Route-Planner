"""
Unit Tests for Graph Construction and Fallback Network Loader.
"""

import unittest
from core.graph_loader import create_fallback_graph
from core.heuristic import haversine_distance, time_heuristic
from core.cost_calculator import get_edge_cost, calculate_travel_time


class TestGraph(unittest.TestCase):
    """Test suite for graph structure, node attributes, and heuristics."""

    def setUp(self):
        self.graph = create_fallback_graph(num_nodes=50, seed=42)

    def test_node_attributes(self):
        """Verify all graph nodes possess geographical coordinates."""
        for n, data in self.graph.nodes.items():
            self.assertIn("x", data)
            self.assertIn("y", data)
            self.assertIsInstance(data["x"], (int, float))
            self.assertIsInstance(data["y"], (int, float))

    def test_edge_attributes(self):
        """Verify edge weights, highway types, and travel times."""
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            self.assertIn("length", data)
            self.assertGreater(data["length"], 0.0)
            self.assertIn("travel_time", data)
            self.assertGreater(data["travel_time"], 0.0)

    def test_haversine_formula(self):
        """Verify haversine distance calculation matches expected geometric range."""
        # Dublin city center to nearby point (~100m)
        dist = haversine_distance(53.3498, -6.2603, 53.3508, -6.2603)
        self.assertAlmostEqual(dist, 111.2, delta=10.0)

    def test_cost_calculator(self):
        """Test edge cost retrieval."""
        edge = list(self.graph.edges(keys=True))[0]
        cost = get_edge_cost(self.graph, edge[0], edge[1], edge[2], weight_attr="length")
        self.assertGreater(cost, 0.0)

        # Test missing edge
        missing = get_edge_cost(self.graph, 9999, 8888)
        self.assertEqual(missing, float("inf"))


if __name__ == "__main__":
    unittest.main()

