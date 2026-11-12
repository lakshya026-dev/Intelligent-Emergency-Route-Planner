"""
Interactive Folium map creation for emergency route visualization.

Provides the MapVisualizer class for creating dark-themed interactive maps
with route overlays, markers, closed roads, and toggleable layer controls.
"""

import folium
from folium import FeatureGroup, Marker, PolyLine, Icon, LayerControl

import config


class MapVisualizer:
    """Creates interactive Folium maps with route overlays and markers."""

    def __init__(self):
        """Initialize with color configuration from config."""
        self.algorithm_colors = config.ALGORITHM_COLORS
        self.closed_road_color = config.CLOSED_ROAD_COLOR

    # ------------------------------------------------------------------ #
    # Base map
    # ------------------------------------------------------------------ #
    def create_base_map(self, center_lat: float, center_lon: float, zoom: int = 13) -> folium.Map:
        """Create a dark-themed Folium map centered on the given coordinates.

        Args:
            center_lat: Latitude of map center.
            center_lon: Longitude of map center.
            zoom: Initial zoom level (default 13).

        Returns:
            A folium.Map object with cartodbdark_matter tiles.
        """
        folium_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom,
            tiles=config.MAP_TILE_STYLE,
            attr=getattr(config, "MAP_TILE_ATTR", "CARTO"),
        )
        return folium_map

    # ------------------------------------------------------------------ #
    # Route drawing
    # ------------------------------------------------------------------ #
    def add_route(
        self,
        folium_map: folium.Map,
        graph,
        path: list,
        algorithm_name: str,
        color: str | None = None,
        weight: int = 5,
        opacity: float = 0.85,
    ) -> None:
        """Draw a polyline for a route path on the map.

        The route is placed in a FeatureGroup named after the algorithm so it
        appears as a toggleable layer in the LayerControl.

        Args:
            folium_map: The Folium map to draw on.
            graph: NetworkX graph with node attributes 'y' (lat) and 'x' (lon).
            path: Ordered list of node IDs forming the route.
            algorithm_name: Name of the algorithm (used for layer name and popup).
            color: Line color (hex). Falls back to config color for the algorithm.
            weight: Line weight in pixels.
            opacity: Line opacity (0–1).
        """
        if not path or len(path) < 2:
            return

        # Resolve color
        if color is None:
            color = self.algorithm_colors.get(algorithm_name, "#ffffff")

        # Reconstruct the route from each traversed edge's stored road shape.
        # For directed MultiDiGraphs, choose the shortest parallel edge, which
        # matches the routing graph's node-to-node path representation.
        coords = []
        selected_edges = []
        for u, v in zip(path, path[1:]):
            edge_bundle = graph.get_edge_data(u, v)
            if not edge_bundle:
                continue
            candidates = list(edge_bundle.values()) if all(isinstance(d, dict) for d in edge_bundle.values()) else [edge_bundle]
            edge_data = min(candidates, key=lambda d: float(d.get("length", float("inf"))))
            selected_edges.append(edge_data)
            shape = edge_data.get("geometry_coords")
            if not shape:
                geometry = edge_data.get("geometry")
                if geometry is not None and hasattr(geometry, "coords"):
                    shape = [(lat, lon) for lon, lat in geometry.coords]
            if not shape:
                shape = [
                    (graph.nodes[u]["y"], graph.nodes[u]["x"]),
                    (graph.nodes[v]["y"], graph.nodes[v]["x"]),
                ]
            shape = [(float(lat), float(lon)) for lat, lon in shape]
            # OSM edge geometry follows u -> v. Reverse only if its endpoints
            # show that it was stored in the opposite direction.
            u_coord = (float(graph.nodes[u]["y"]), float(graph.nodes[u]["x"]))
            if shape and abs(shape[0][0]-u_coord[0]) + abs(shape[0][1]-u_coord[1]) > abs(shape[-1][0]-u_coord[0]) + abs(shape[-1][1]-u_coord[1]):
                shape.reverse()
            coords.extend(shape if not coords else shape[1:])

        if len(coords) < 2:
            return

        # Calculate route distance safely
        total_distance = 0.0
        total_distance = sum(float(edge.get("length", 0.0)) for edge in selected_edges)

        # Format popup
        dist_str = f"{total_distance / 1000:.2f} km" if total_distance >= 1000 else f"{total_distance:.0f} m"
        popup_html = (
            f"<b>{algorithm_name} Route</b><br>"
            f"Distance: {dist_str}<br>"
            f"Waypoints: {len(path)} nodes"
        )

        # Create feature group and add polyline
        fg = FeatureGroup(name=f"{algorithm_name} Route", show=True)
        PolyLine(
            locations=coords,
            color=color,
            weight=weight,
            opacity=opacity,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{algorithm_name}: {dist_str}",
        ).add_to(fg)

        fg.add_to(folium_map)

    # ------------------------------------------------------------------ #
    # Markers
    # ------------------------------------------------------------------ #
    def add_markers(self, folium_map: folium.Map, graph, start_node, end_node) -> None:
        """Add start (green) and end (red) markers to the map.

        Args:
            folium_map: The Folium map.
            graph: NetworkX graph with node coordinate attributes.
            start_node: Node ID for the start location.
            end_node: Node ID for the end location.
        """
        if start_node is None or end_node is None:
            return
        if start_node not in graph.nodes or end_node not in graph.nodes:
            return

        start_lat = graph.nodes[start_node]["y"]
        start_lon = graph.nodes[start_node]["x"]
        end_lat = graph.nodes[end_node]["y"]
        end_lon = graph.nodes[end_node]["x"]

        Marker(
            location=[start_lat, start_lon],
            popup=folium.Popup(
                f"<b>Start</b><br>Node: {start_node}<br>"
                f"Lat: {start_lat:.6f}<br>Lon: {start_lon:.6f}",
                max_width=250,
            ),
            icon=Icon(color="green", icon="play", prefix="fa"),
            tooltip="Start",
        ).add_to(folium_map)

        Marker(
            location=[end_lat, end_lon],
            popup=folium.Popup(
                f"<b>End</b><br>Node: {end_node}<br>"
                f"Lat: {end_lat:.6f}<br>Lon: {end_lon:.6f}",
                max_width=250,
            ),
            icon=Icon(color="red", icon="stop", prefix="fa"),
            tooltip="End",
        ).add_to(folium_map)

    # ------------------------------------------------------------------ #
    # Closed roads
    # ------------------------------------------------------------------ #
    def add_closed_roads(self, folium_map: folium.Map, graph, closed_roads: list) -> None:
        """Draw closed-road segments as red dashed lines.

        Args:
            folium_map: The Folium map.
            graph: NetworkX graph.
            closed_roads: List of (u, v) tuples representing closed edges.
        """
        if not closed_roads:
            return

        fg = FeatureGroup(name="Closed Roads")
        for edge in closed_roads:
            try:
                u, v = edge[0], edge[1]
                source_graph = getattr(graph, "_original_graph", graph)
                edge_bundle = source_graph.get_edge_data(u, v) or {}
                edge_data = edge_bundle.get(edge[2]) if len(edge) > 2 else None
                if edge_data is None and edge_bundle:
                    edge_data = next(iter(edge_bundle.values()))
                shape = edge_data.get("geometry_coords") if edge_data else None
                if not shape:
                    shape = [(graph.nodes[u]["y"], graph.nodes[u]["x"]), (graph.nodes[v]["y"], graph.nodes[v]["x"])]
            except (KeyError, IndexError, TypeError):
                continue

            PolyLine(
                locations=shape,
                color=self.closed_road_color,
                weight=4,
                opacity=0.9,
                dash_array="10 6",
                popup="Road Closed",
                tooltip="Closed Road",
            ).add_to(fg)

        fg.add_to(folium_map)

    # ------------------------------------------------------------------ #
    # Layer control
    # ------------------------------------------------------------------ #
    def add_layer_control(self, folium_map: folium.Map) -> None:
        """Add a LayerControl to the map so users can toggle layers.

        Args:
            folium_map: The Folium map.
        """
        LayerControl(collapsed=False).add_to(folium_map)

    # ------------------------------------------------------------------ #
    # All-in-one convenience method
    # ------------------------------------------------------------------ #
    def create_route_map(
        self,
        graph,
        results_dict: dict,
        start_node,
        end_node,
        closed_roads: list | None = None,
        center_lat: float | None = None,
        center_lon: float | None = None,
    ) -> folium.Map:
        """Create a complete route comparison map.

        Combines base map creation, markers, route overlays, closed roads, and
        layer control into a single call.

        Args:
            graph: NetworkX graph.
            results_dict: Dict mapping algorithm_name -> AlgorithmResult.
            start_node: Start node ID.
            end_node: End node ID.
            closed_roads: Optional list of (u, v) closed edges.
            center_lat: Optional map center latitude (defaults to start node).
            center_lon: Optional map center longitude (defaults to start node).

        Returns:
            A fully-populated folium.Map object.
        """
        # Determine map center
        if center_lat is None or center_lon is None:
            if start_node is not None and start_node in graph.nodes:
                center_lat = graph.nodes[start_node]["y"]
                center_lon = graph.nodes[start_node]["x"]
            elif len(graph.nodes) > 0:
                first_node = next(iter(graph.nodes.keys()))
                center_lat = graph.nodes[first_node]["y"]
                center_lon = graph.nodes[first_node]["x"]
            else:
                center_lat, center_lon = 53.3498, -6.2603

        folium_map = self.create_base_map(center_lat, center_lon)

        # Markers
        self.add_markers(folium_map, graph, start_node, end_node)

        # Routes
        for algo_name, result in results_dict.items():
            if result.found and result.path:
                self.add_route(folium_map, graph, result.path, algo_name)

        # Closed roads
        if closed_roads:
            self.add_closed_roads(folium_map, graph, closed_roads)

        # Layer control
        self.add_layer_control(folium_map)

        # Automatically adjust map bounds to show complete calculated route and markers
        bounds_lats = []
        bounds_lons = []

        # 1. Add route coordinates
        for result in results_dict.values():
            if result.found and result.path:
                for u, v in zip(result.path, result.path[1:]):
                    bundle = graph.get_edge_data(u, v) or {}
                    edge = min(bundle.values(), key=lambda d: float(d.get("length", float("inf")))) if bundle else {}
                    shape = edge.get("geometry_coords") or [(graph.nodes[u]["y"], graph.nodes[u]["x"]), (graph.nodes[v]["y"], graph.nodes[v]["x"])]
                    bounds_lats.extend(float(p[0]) for p in shape)
                    bounds_lons.extend(float(p[1]) for p in shape)

        # 2. Add start/end markers
        if start_node is not None and start_node in graph.nodes:
            bounds_lats.append(float(graph.nodes[start_node]["y"]))
            bounds_lons.append(float(graph.nodes[start_node]["x"]))
        if end_node is not None and end_node in graph.nodes:
            bounds_lats.append(float(graph.nodes[end_node]["y"]))
            bounds_lons.append(float(graph.nodes[end_node]["x"]))

        # Fit bounds if coordinates exist
        if bounds_lats and bounds_lons:
            min_lat, max_lat = min(bounds_lats), max(bounds_lats)
            min_lon, max_lon = min(bounds_lons), max(bounds_lons)
            # Add small padding if nodes are very close
            if abs(max_lat - min_lat) < 0.001:
                min_lat -= 0.003
                max_lat += 0.003
            if abs(max_lon - min_lon) < 0.001:
                min_lon -= 0.003
                max_lon += 0.003
            folium_map.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

        return folium_map
