"""
Unit Tests for Central Route Optimizer and Comparison Services.
"""

import unittest
from core.graph_loader import create_fallback_graph
from core.route_optimizer import RouteOptimizer
from simulation.traffic_simulator import TrafficSimulator
from simulation.road_closures import RoadClosureManager
from simulation.emergency_priority import EmergencyPriorityManager
from services.comparison_service import ComparisonService


class TestRouteOptimizer(unittest.TestCase):
    """Test suite for orchestrating multi-algorithm evaluation."""

    def setUp(self):
        self.graph = create_fallback_graph(num_nodes=40, seed=42)
        self.optimizer = RouteOptimizer(self.graph)
        self.traffic_sim = TrafficSimulator()
        self.closure_mgr = RoadClosureManager()
        self.emergency_mgr = EmergencyPriorityManager()

    def test_compare_all_algorithms(self):
        """Test executing all 4 algorithms on identical graph state."""
        prep_graph = self.optimizer.prepare_graph(
            traffic_condition="Moderate",
            vehicle_type="Fire Truck",
            traffic_simulator=self.traffic_sim,
            emergency_manager=self.emergency_mgr,
        )

        results = self.optimizer.compare_algorithms(
            prep_graph,
            start=0,
            goal=20,
            weight_attr="traffic_travel_time",
            algorithms=["BFS", "DFS", "Greedy", "A*"],
        )

        self.assertEqual(len(results), 4)
        for algo in ["BFS", "DFS", "Greedy", "A*"]:
            self.assertIn(algo, results)
            self.assertTrue(results[algo].found)

    def test_unreachable_due_to_closures(self):
        """Test path discovery failure when all outgoing edges of start are closed."""
        prep_graph = self.graph.copy()
        for v in list(prep_graph.neighbors(0)):
            prep_graph.remove_edge(0, v)

        res = self.optimizer.find_route(prep_graph, start=0, goal=10, algorithm="A*")
        self.assertFalse(res.found)
        self.assertEqual(res.path, [])

    def test_comparison_service(self):
        """Test summary and table generation."""
        results = self.optimizer.compare_algorithms(
            self.graph, start=0, goal=15, weight_attr="length"
        )
        comp = ComparisonService()
        df = comp.compare_results(results)
        self.assertFalse(df.empty)

        best = comp.get_best_algorithm(results, metric="total_distance")
        self.assertIn(best, ["BFS", "DFS", "Greedy", "A*"])


if __name__ == "__main__":
    unittest.main()

