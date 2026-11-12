"""Collapsible operations controls for the route planner dashboard."""

import streamlit as st
import config
from services.location_service import get_graph_nodes_as_options, get_random_start_end, randomize_route_coordinates


def render_sidebar(graph=None):
    st.sidebar.markdown(
        '<div class="sidebar-brand"><span>✦</span><div><b>DISPATCH CONTROLS</b><small>Emergency operations</small></div></div>',
        unsafe_allow_html=True,
    )
    cities = list(config.SUPPORTED_CITIES)
    default_city_idx = cities.index(config.DEFAULT_CITY) if config.DEFAULT_CITY in cities else 0
    with st.sidebar.expander("01 · CITY & NETWORK", expanded=True):
        selected_city = st.selectbox("Area / City Network", cities, index=default_city_idx)

    start_node = goal_node = None
    with st.sidebar.expander("02 · ROUTE COORDINATES", expanded=True):
        if graph is not None and graph.number_of_nodes():
            options = get_graph_nodes_as_options(graph, max_nodes=300)
            node_ids = [item[0] for item in options]
            labels = {item[0]: item[1] for item in options}
            for key in ("sb_start_node", "sb_goal_node", "start_node", "goal_node"):
                if key in st.session_state and st.session_state[key] not in node_ids:
                    del st.session_state[key]
            if "start_node" not in st.session_state:
                start, goal = get_random_start_end(graph, seed=42)
                st.session_state.start_node = start if start in node_ids else node_ids[0]
                st.session_state.goal_node = goal if goal in node_ids else node_ids[-1]
            # Widget state must be valid before selectboxes are instantiated.
            if st.session_state.get("sb_start_node") not in node_ids:
                st.session_state.sb_start_node = st.session_state.start_node if st.session_state.start_node in node_ids else node_ids[0]
            if st.session_state.get("sb_goal_node") not in node_ids:
                st.session_state.sb_goal_node = st.session_state.goal_node if st.session_state.goal_node in node_ids else node_ids[-1]
            if st.session_state.sb_start_node == st.session_state.sb_goal_node and len(node_ids) > 1:
                st.session_state.sb_goal_node = next(node for node in node_ids if node != st.session_state.sb_start_node)
            # The keys are initialized above; don't also pass index= because
            # Streamlit treats that as a second default for an existing key.
            start_node = st.selectbox("Origin · Dispatch", node_ids,
                                      format_func=lambda nid: labels.get(nid, str(nid)), key="sb_start_node")
            goal_node = st.selectbox("Destination · Incident", node_ids,
                                     format_func=lambda nid: labels.get(nid, str(nid)), key="sb_goal_node")
            st.session_state.start_node = start_node
            st.session_state.goal_node = goal_node
            st.button("🎲 Randomize coordinates", use_container_width=True,
                      on_click=randomize_route_coordinates, args=(graph, node_ids),
                      disabled=len(node_ids) < 2)
            if st.session_state.get("coordinate_randomize_error"):
                st.warning(st.session_state.coordinate_randomize_error)
        else:
            st.info("Road network is loading.")

    with st.sidebar.expander("03 · RESPONSE PROFILE", expanded=True):
        vehicles = list(config.EMERGENCY_VEHICLES)
        vehicle_idx = st.radio("Emergency vehicle", range(len(vehicles)),
                               format_func=lambda idx: f"{config.EMERGENCY_VEHICLES[vehicles[idx]]['icon']} {vehicles[idx]}")
        selected_vehicle = vehicles[vehicle_idx]
        vehicle_info = config.EMERGENCY_VEHICLES[selected_vehicle]
        st.caption(f"Priority level {vehicle_info['priority']} · Siren speed factor {vehicle_info['speed_factor']}×")
        objectives = list(config.OPTIMIZATION_OBJECTIVES)
        selected_objective = st.selectbox("Routing objective", objectives, index=min(2, len(objectives) - 1))

    with st.sidebar.expander("04 · LIVE TRAFFIC", expanded=True):
        traffic_levels = list(config.TRAFFIC_CONDITIONS)
        selected_traffic = st.select_slider("Congestion level", traffic_levels, value="Moderate")
        traffic_info = config.TRAFFIC_CONDITIONS[selected_traffic]
        st.markdown(
            f'<div class="traffic-readout"><i style="background:{traffic_info["color"]}"></i><b>{selected_traffic}</b>'
            f'<span>{traffic_info["multiplier"]}× travel time</span></div><small>{traffic_info["description"]}</small>',
            unsafe_allow_html=True,
        )

    with st.sidebar.expander("05 · ROAD CLOSURES", expanded=False):
        if "closed_roads" not in st.session_state:
            st.session_state.closed_roads = []
        enabled = st.checkbox("Enable road incident / blockade", value=bool(st.session_state.closed_roads))
        if enabled and graph is not None:
            edges = list(graph.edges(keys=True))[:50]
            labels = {edge: f"Segment {edge[0]} → {edge[1]}" for edge in edges}
            selected_closures = st.multiselect("Segments to close", edges,
                                               default=[edge for edge in st.session_state.closed_roads if edge in edges],
                                               format_func=lambda edge: labels.get(edge, str(edge)))
            st.session_state.closed_roads = selected_closures
        else:
            st.session_state.closed_roads = []

    with st.sidebar.expander("06 · ROUTING ENGINE", expanded=True):
        st.caption("Calculate a route or compare all four search strategies.")
        col_a, col_b = st.columns(2)
        btn_bfs = col_a.button("🔵 BFS", use_container_width=True, help="Blue route")
        btn_dfs = col_b.button("🟠 DFS", use_container_width=True, help="Orange route")
        col_c, col_d = st.columns(2)
        btn_greedy = col_c.button("🟣 Greedy", use_container_width=True, help="Purple route")
        btn_astar = col_d.button("🟢 A*", use_container_width=True, help="Green route")
        btn_compare = st.button("📊 Benchmark all four", use_container_width=True)

    clicked_algo = ("BFS" if btn_bfs else "DFS" if btn_dfs else "Greedy" if btn_greedy
                    else "A*" if btn_astar else "ALL" if btn_compare else None)
    return {
        "city": selected_city, "vehicle_type": selected_vehicle,
        "objective": selected_objective, "traffic_condition": selected_traffic,
        "start_node": start_node, "goal_node": goal_node,
        "closed_roads": st.session_state.closed_roads, "clicked_algo": clicked_algo,
    }
