"""
Unit Tests for Traffic and Road Closure Simulations.
"""

import unittest
from core.graph_loader import create_fallback_graph
from simulation.traffic_simulator import TrafficSimulator
from simulation.road_closures import RoadClosureManager
from simulation.emergency_priority import EmergencyPriorityManager
import config


class TestTrafficSimulation(unittest.TestCase):
    """Test suite for traffic simulation and road closures."""

    def setUp(self):
        self.graph = create_fallback_graph(num_nodes=30, seed=42)
        self.traffic_sim = TrafficSimulator(seed=config.TRAFFIC_RANDOM_SEED)
        self.closure_mgr = RoadClosureManager()
        self.emergency_mgr = EmergencyPriorityManager()

    def test_uniform_traffic_multipliers(self):
        """Test applying uniform traffic conditions to road network."""
        prep = self.traffic_sim.generate_traffic(self.graph, condition="Heavy")
        mult = config.TRAFFIC_CONDITIONS["Heavy"]["multiplier"]

        for u, v, key, data in prep.edges(keys=True, data=True):
            self.assertEqual(data.get("traffic_multiplier"), mult)
            base_time = self.graph.get_edge_data(u, v, key).get("travel_time", 0)
            self.assertAlmostEqual(data.get("traffic_travel_time"), base_time * mult, places=4)

    def test_road_closures(self):
        """Test adding and removing road closures."""
        edge = list(self.graph.edges(keys=True))[0]
        u, v, key = edge[0], edge[1], edge[2] if len(edge) > 2 else 0

        self.closure_mgr.close_road(u, v, key)
        self.assertTrue(self.closure_mgr.is_closed(u, v, key))
        self.assertEqual(self.closure_mgr.get_closure_count(), 1)

        closed_graph = self.closure_mgr.apply_closures(self.graph)
        self.assertFalse(closed_graph.has_edge(u, v, key))

        # Reopen road
        self.closure_mgr.open_road(u, v, key)
        self.assertFalse(self.closure_mgr.is_closed(u, v, key))
        self.assertEqual(self.closure_mgr.get_closure_count(), 0)

    def test_emergency_vehicle_speed_factor(self):
        """Test vehicle speed adjustment on travel times."""
        prep = self.emergency_mgr.apply_priority(self.graph, vehicle_type="Ambulance")
        factor = config.EMERGENCY_VEHICLES["Ambulance"]["speed_factor"]

        for u, v, key, data in prep.edges(keys=True, data=True):
            orig_time = self.graph.get_edge_data(u, v, key).get("travel_time", 0)
            self.assertAlmostEqual(data.get("travel_time"), orig_time / factor, places=4)


if __name__ == "__main__":
    unittest.main()

