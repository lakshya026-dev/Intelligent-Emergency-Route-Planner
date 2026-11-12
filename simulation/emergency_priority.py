"""
Emergency Vehicle Priority Manager.

Adjusts graph travel times based on the speed advantages that
emergency vehicles have (sirens, right-of-way, etc.).
"""

import config


class EmergencyPriorityManager:
    """Manages emergency-vehicle priority adjustments on a road graph."""

    def __init__(self):
        """Load vehicle configurations from ``config.EMERGENCY_VEHICLES``."""
        self._vehicles: dict = config.EMERGENCY_VEHICLES

    # ------------------------------------------------------------------ #
    #  Queries
    # ------------------------------------------------------------------ #
    def get_vehicle_types(self) -> list[str]:
        """
        Return a list of available emergency-vehicle type names.

        Returns:
            e.g. ``['Ambulance', 'Fire Truck', 'Rescue Vehicle']``
        """
        return list(self._vehicles.keys())

    def get_vehicle_config(self, vehicle_type: str) -> dict:
        """
        Return the full configuration dict for a vehicle type.

        Args:
            vehicle_type: One of the keys from ``config.EMERGENCY_VEHICLES``.

        Returns:
            Dict with keys such as ``icon``, ``priority``,
            ``speed_factor``, ``color``, ``description``.

        Raises:
            ValueError: If *vehicle_type* is unknown.
        """
        if vehicle_type not in self._vehicles:
            raise ValueError(
                f"Unknown vehicle type '{vehicle_type}'. "
                f"Valid types: {list(self._vehicles.keys())}"
            )
        return dict(self._vehicles[vehicle_type])

    # ------------------------------------------------------------------ #
    #  Graph adjustment
    # ------------------------------------------------------------------ #
    def apply_priority(self, graph, vehicle_type: str):
        """
        Adjust travel times on a **copy** of the graph for *vehicle_type*.

        Each edge's ``travel_time`` (and ``traffic_travel_time`` if present)
        is divided by the vehicle's ``speed_factor``, reflecting that
        emergency vehicles can move faster than normal traffic.

        Args:
            graph: A NetworkX MultiDiGraph.
            vehicle_type: Key from ``config.EMERGENCY_VEHICLES``.

        Returns:
            A modified copy of the graph.

        Raises:
            ValueError: If *vehicle_type* is unknown.
        """
        if vehicle_type not in self._vehicles:
            raise ValueError(
                f"Unknown vehicle type '{vehicle_type}'. "
                f"Valid types: {list(self._vehicles.keys())}"
            )

        speed_factor = self._vehicles[vehicle_type]["speed_factor"]
        g = graph.copy()

        for u, v, key, data in g.edges(keys=True, data=True):
            if "travel_time" in data:
                g[u][v][key]["travel_time"] = data["travel_time"] / speed_factor
            if "traffic_travel_time" in data:
                g[u][v][key]["traffic_travel_time"] = (
                    data["traffic_travel_time"] / speed_factor
                )

        return g

    # ------------------------------------------------------------------ #
    #  Optimization objectives
    # ------------------------------------------------------------------ #
    @staticmethod
    def get_optimization_objectives() -> dict:
        """
        Return the available optimization objectives from config.

        Returns:
            ``config.OPTIMIZATION_OBJECTIVES`` dict.
        """
        return config.OPTIMIZATION_OBJECTIVES
