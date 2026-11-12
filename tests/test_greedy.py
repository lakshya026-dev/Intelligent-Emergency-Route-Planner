"""
Unit Tests for Greedy Best-First Search Algorithm.
"""

import unittest
from core.graph_loader import create_fallback_graph
from algorithms.greedy import greedy_search


class TestGreedy(unittest.TestCase):
    """Test suite for Greedy Best-First Search."""

    def setUp(self):
        self.graph = create_fallback_graph(num_nodes=40, seed=42)

    def test_start_equals_goal(self):
        """Test search when origin is identical to destination."""
        res = greedy_search(self.graph, start=5, goal=5)
        self.assertTrue(res.found)
        self.assertEqual(res.path, [5])
        self.assertEqual(res.total_distance, 0.0)

    def test_valid_path_found(self):
        """Test discovering a path using heuristic straight-line distance."""
        res = greedy_search(self.graph, start=0, goal=20)
        self.assertTrue(res.found)
        self.assertEqual(res.path[0], 0)
        self.assertEqual(res.path[-1], 20)
        self.assertGreater(res.total_distance, 0.0)
        self.assertGreater(res.nodes_explored, 0)

    def test_heuristic_efficiency(self):
        """Test that Greedy explores fewer nodes than an uninformed search in many cases."""
        res = greedy_search(self.graph, start=0, goal=30)
        self.assertTrue(res.found)
        self.assertLessEqual(res.nodes_explored, len(self.graph.nodes))

    def test_invalid_nodes(self):
        """Test search with nonexistent nodes."""
        res = greedy_search(self.graph, start=9999, goal=0)
        self.assertFalse(res.found)


if __name__ == "__main__":
    unittest.main()

