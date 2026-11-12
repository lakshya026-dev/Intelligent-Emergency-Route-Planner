"""
Road Closure Simulation.

Manages a set of closed roads and applies closures to a graph by
returning a new graph with the closed edges removed.
"""


class RoadClosureManager:
    """Tracks closed roads and applies closures to a graph copy."""

    def __init__(self):
        """Initialize with an empty set of closed roads."""
        self._closed_roads: set[tuple] = set()

    def close_road(self, u, v, key=0):
        """
        Mark a road as closed.

        Args:
            u: Start node of the edge.
            v: End node of the edge.
            key: Edge key (default 0).
        """
        self._closed_roads.add((u, v, key))

    # Alias for convenience
    add_closure = close_road

    def open_road(self, u, v, key=0):
        """
        Re-open a previously closed road.

        Args:
            u: Start node of the edge.
            v: End node of the edge.
            key: Edge key (default 0).
        """
        self._closed_roads.discard((u, v, key))

    def clear_all(self):
        """Remove all road closures."""
        self._closed_roads.clear()

    # ------------------------------------------------------------------ #
    #  Queries
    # ------------------------------------------------------------------ #
    def is_closed(self, u, v, key=0) -> bool:
        """
        Check whether a specific road is closed.

        Args:
            u: Start node of the edge.
            v: End node of the edge.
            key: Edge key (default 0).

        Returns:
            True if the road is currently closed.
        """
        return (u, v, key) in self._closed_roads

    def get_closed_roads(self) -> list[tuple]:
        """
        Return a list of all currently closed roads.

        Returns:
            List of ``(u, v, key)`` tuples.
        """
        return list(self._closed_roads)

    def get_closure_count(self) -> int:
        """
        Return the number of currently closed roads.

        Returns:
            Integer count.
        """
        return len(self._closed_roads)

    # ------------------------------------------------------------------ #
    #  Graph application
    # ------------------------------------------------------------------ #
    def apply_closures(self, graph):
        """
        Return a **new** graph with all closed edges removed.

        The original graph is never modified.

        Args:
            graph: A NetworkX MultiDiGraph.

        Returns:
            A copy of *graph* with closed edges removed.
        """
        g = graph.copy()

        for u, v, key in self._closed_roads:
            if g.has_edge(u, v, key=key):
                g.remove_edge(u, v, key=key)

        return g
