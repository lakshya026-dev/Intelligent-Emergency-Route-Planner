"""Tests for callback-based route-coordinate randomization."""

import unittest

import networkx as nx
import streamlit as st

from services.location_service import randomize_route_coordinates


class TestRandomRouteCoordinates(unittest.TestCase):
    def setUp(self):
        for key in ("sb_start_node", "sb_goal_node", "start_node", "goal_node", "coordinate_randomize_error"):
            st.session_state.pop(key, None)

    def test_callback_selects_distinct_nodes_from_graph(self):
        graph = nx.path_graph(5)
        for _ in range(20):
            randomize_route_coordinates(graph, list(graph.nodes))
            start, goal = st.session_state.sb_start_node, st.session_state.sb_goal_node
            self.assertIn(start, graph)
            self.assertIn(goal, graph)
            self.assertNotEqual(start, goal)
            self.assertEqual(start, st.session_state.start_node)
            self.assertEqual(goal, st.session_state.goal_node)
            self.assertIsNone(st.session_state.coordinate_randomize_error)

    def test_callback_handles_graph_with_fewer_than_two_nodes(self):
        graph = nx.empty_graph(1)
        randomize_route_coordinates(graph, list(graph.nodes))
        self.assertEqual(st.session_state.coordinate_randomize_error,
                         "At least two road-network intersections are required.")
        self.assertNotIn("sb_start_node", st.session_state)
        self.assertNotIn("sb_goal_node", st.session_state)

    def test_callback_handles_missing_graph(self):
        randomize_route_coordinates(None, [])
        self.assertEqual(st.session_state.coordinate_randomize_error,
                         "At least two road-network intersections are required.")


if __name__ == "__main__":
    unittest.main()
