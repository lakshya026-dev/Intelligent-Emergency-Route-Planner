"""
Unit Tests for Depth-First Search (DFS) Algorithm.
"""

import unittest
from core.graph_loader import create_fallback_graph
from algorithms.dfs import dfs_search


class TestDFS(unittest.TestCase):
    """Test suite for DFS pathfinding."""

    def setUp(self):
        self.graph = create_fallback_graph(num_nodes=30, seed=42)

    def test_start_equals_goal(self):
        """Test search when origin is identical to destination."""
        res = dfs_search(self.graph, start=0, goal=0)
        self.assertTrue(res.found)
        self.assertEqual(res.path, [0])
        self.assertEqual(res.total_distance, 0.0)

    def test_valid_path_found(self):
        """Test discovering a path between connected nodes."""
        res = dfs_search(self.graph, start=0, goal=10)
        self.assertTrue(res.found)
        self.assertGreater(len(res.path), 1)
        self.assertEqual(res.path[0], 0)
        self.assertEqual(res.path[-1], 10)
        self.assertGreater(res.nodes_explored, 0)

    def test_invalid_nodes(self):
        """Test search with nonexistent nodes."""
        res1 = dfs_search(self.graph, start=-1, goal=10)
        self.assertFalse(res1.found)
        res2 = dfs_search(self.graph, start=0, goal=-1)
        self.assertFalse(res2.found)

    def test_cyclic_graph_handling(self):
        """Test that DFS does not enter infinite loops on cyclic graphs."""
        res = dfs_search(self.graph, start=0, goal=15)
        self.assertTrue(res.found)
        # Check no node appears twice in the simple path
        self.assertEqual(len(res.path), len(set(res.path)))


if __name__ == "__main__":
    unittest.main()

