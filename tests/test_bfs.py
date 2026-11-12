"""
Unit Tests for Breadth-First Search (BFS) Algorithm.
"""

import unittest
from core.graph_loader import create_fallback_graph
from algorithms.bfs import bfs_search


class TestBFS(unittest.TestCase):
    """Test suite for BFS pathfinding."""

    def setUp(self):
        self.graph = create_fallback_graph(num_nodes=30, seed=42)

    def test_start_equals_goal(self):
        """Test search when origin is identical to destination."""
        res = bfs_search(self.graph, start=0, goal=0)
        self.assertTrue(res.found)
        self.assertEqual(res.path, [0])
        self.assertEqual(res.total_distance, 0.0)
        self.assertEqual(res.total_travel_time, 0.0)
        self.assertEqual(res.nodes_explored, 1)

    def test_valid_path_found(self):
        """Test discovering a path between connected nodes."""
        res = bfs_search(self.graph, start=0, goal=10)
        self.assertTrue(res.found)
        self.assertGreater(len(res.path), 1)
        self.assertEqual(res.path[0], 0)
        self.assertEqual(res.path[-1], 10)
        self.assertGreater(res.total_distance, 0.0)
        self.assertGreater(res.nodes_explored, 0)
        self.assertGreater(res.edges_traversed, 0)

    def test_invalid_start_node(self):
        """Test search when start node does not exist."""
        res = bfs_search(self.graph, start=99999, goal=10)
        self.assertFalse(res.found)
        self.assertEqual(res.path, [])

    def test_invalid_goal_node(self):
        """Test search when goal node does not exist."""
        res = bfs_search(self.graph, start=0, goal=99999)
        self.assertFalse(res.found)
        self.assertEqual(res.path, [])

    def test_unreachable_node(self):
        """Test search when goal is isolated (disconnected)."""
        isolated_g = self.graph.copy()
        isolated_g.add_node(999, y=53.35, x=-6.26)  # isolated node, no edges
        res = bfs_search(isolated_g, start=0, goal=999)
        self.assertFalse(res.found)
        self.assertEqual(res.path, [])


if __name__ == "__main__":
    unittest.main()

