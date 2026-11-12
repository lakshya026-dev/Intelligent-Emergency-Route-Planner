"""
Unit Tests for A* Search Algorithm.
"""

import unittest
from core.graph_loader import create_fallback_graph
from algorithms.astar import astar_search
from algorithms.bfs import bfs_search


class TestAStar(unittest.TestCase):
    """Test suite for A* search optimality and admissibility."""

    def setUp(self):
        self.graph = create_fallback_graph(num_nodes=50, seed=42)

    def test_start_equals_goal(self):
        """Test search when origin is identical to destination."""
        res = astar_search(self.graph, start=10, goal=10)
        self.assertTrue(res.found)
        self.assertEqual(res.path, [10])
        self.assertEqual(res.total_distance, 0.0)

    def test_valid_optimal_path(self):
        """Test that A* finds a valid path to destination."""
        res = astar_search(self.graph, start=0, goal=25, weight_attr="length")
        self.assertTrue(res.found)
        self.assertEqual(res.path[0], 0)
        self.assertEqual(res.path[-1], 25)
        self.assertGreater(res.total_distance, 0.0)

    def test_distance_optimality(self):
        """Test that A* distance is <= BFS distance (as BFS optimizes hops, not distance)."""
        start, goal = 0, 35
        res_astar = astar_search(self.graph, start=start, goal=goal, weight_attr="length")
        res_bfs = bfs_search(self.graph, start=start, goal=goal, weight_attr="length")

        self.assertTrue(res_astar.found)
        self.assertTrue(res_bfs.found)
        # A* distance must be less than or equal to BFS distance
        self.assertLessEqual(res_astar.total_distance, res_bfs.total_distance + 1e-4)

    def test_time_objective(self):
        """Test A* search under travel_time objective."""
        res = astar_search(self.graph, start=0, goal=20, weight_attr="travel_time")
        self.assertTrue(res.found)
        self.assertGreater(res.total_travel_time, 0.0)

    def test_invalid_nodes(self):
        """Test handling of invalid node IDs."""
        res = astar_search(self.graph, start=99999, goal=10)
        self.assertFalse(res.found)


if __name__ == "__main__":
    unittest.main()

