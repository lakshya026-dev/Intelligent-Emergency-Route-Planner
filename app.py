"""
Intelligent Emergency Route Planner
CSE276 – Artificial Intelligence Foundations | Continuous Assessment 1 Project

Interactive Master Operations Dashboard.
Features:
- Drivable road network graph (OpenStreetMap + offline Dublin fallback)
- Real-time interactive map visible at all times
- One-click triggers for BFS (Blue), DFS (Orange), Greedy (Purple), and A* (Green)
- Dynamic replacement of previous routes on algorithm selection
- Live display of Route Distance, Travel Time, Execution Time, and Nodes Explored
- Strict exclusion of closed roads and traffic congestion simulation
"""

from pathlib import Path
import streamlit as st

import config
from core.graph_loader import load_graph
from core.route_optimizer import RouteOptimizer
from simulation.traffic_simulator import TrafficSimulator
from simulation.road_closures import RoadClosureManager
from simulation.emergency_priority import EmergencyPriorityManager
from services.map_service import get_city_center
from services.comparison_service import ComparisonService
from visualization.map_visualizer import MapVisualizer
from visualization.charts import create_traffic_distribution_chart
from visualization.metrics import (
    format_distance,
    format_time,
    format_execution_time,
    format_nodes,
    get_algorithm_emoji,
)

# UI Components
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard_header
from components.map_component import render_map
from components.algorithm_comparison import render_comparison
from components.statistics import render_statistics


# ─────────────────────────────────────────────────────────────────────────────
# 1. Page Configuration & Custom CSS Injection
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Emergency Route Planner | CSE276",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_custom_css():
    """Inject assets/styles.css into the Streamlit app."""
    css_path = Path(__file__).resolve().parent / "assets" / "styles.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()


# ─────────────────────────────────────────────────────────────────────────────
# 2. Cached Road Network Loader
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_cached_graph(city_name: str):
    """
    Load or download the drivable road network for the requested city.
    Loads cached OSM roads or reports a useful download error.
    """
    return load_graph(place_name=city_name, cache=True)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Session State Initialization
# ─────────────────────────────────────────────────────────────────────────────
if "current_city" not in st.session_state:
    st.session_state.current_city = config.DEFAULT_CITY

if "results_dict" not in st.session_state:
    st.session_state.results_dict = {}

if "active_algo" not in st.session_state:
    st.session_state.active_algo = None

if "comparison_df" not in st.session_state:
    st.session_state.comparison_df = None

if "best_algo" not in st.session_state:
    st.session_state.best_algo = None

if "graph" not in st.session_state:
    with st.spinner(f"Loading road network for {st.session_state.current_city}..."):
        st.session_state.graph = get_cached_graph(st.session_state.current_city)

if "prepared_graph" not in st.session_state:
    st.session_state.prepared_graph = st.session_state.graph


# ─────────────────────────────────────────────────────────────────────────────
# 4. Sidebar Controls
# ─────────────────────────────────────────────────────────────────────────────
controls = render_sidebar(graph=st.session_state.graph)

# Handle city change
if controls["city"] != st.session_state.current_city:
    st.session_state.current_city = controls["city"]
    with st.spinner(f"Acquiring road network for {controls['city']}..."):
        st.session_state.graph = get_cached_graph(controls["city"])
        st.session_state.results_dict = {}
        st.session_state.active_algo = None
        st.session_state.comparison_df = None
        st.session_state.best_algo = None
        st.session_state.pop("sb_start_node", None)
        st.session_state.pop("sb_goal_node", None)
        st.session_state.pop("start_node", None)
        st.session_state.pop("goal_node", None)
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# 5. Core Execution Function
# ─────────────────────────────────────────────────────────────────────────────
def execute_algorithm(algo_choice: str):
    """
    Execute selected Python algorithm locally on the prepared road network graph.
    Replaces any previous route so only the active route is displayed on the map.
    """
    s_node = controls["start_node"]
    g_node = controls["goal_node"]

    if s_node is None or g_node is None:
        st.error("Please select valid Start and Destination coordinates in the sidebar.")
        return

    if s_node == g_node:
        st.warning("Origin and Destination are identical (Distance: 0m).")
        return

    # Initialize simulation managers
    traffic_sim = TrafficSimulator(seed=config.TRAFFIC_RANDOM_SEED)
    closure_mgr = RoadClosureManager()
    emergency_mgr = EmergencyPriorityManager()

    weight_attr = config.OPTIMIZATION_OBJECTIVES.get(
        controls["objective"], {"weight_attr": "traffic_travel_time"}
    )["weight_attr"]

    optimizer = RouteOptimizer(st.session_state.graph)

    # Prepare working graph copy: apply traffic, exclude closed roads, factor vehicle priority
    prepared_graph = optimizer.prepare_graph(
        traffic_condition=controls["traffic_condition"],
        vehicle_type=controls["vehicle_type"],
        closed_roads=controls["closed_roads"],
        traffic_simulator=traffic_sim,
        road_closure_manager=closure_mgr,
        emergency_manager=emergency_mgr,
    )
    # Keep original geometry available for drawing incident closures, while
    # routes are always rendered against the prepared (closure-filtered) graph.
    prepared_graph.graph["_original_graph"] = st.session_state.graph
    st.session_state.prepared_graph = prepared_graph

    if algo_choice == "ALL":
        # Run all 4 algorithms for benchmarking
        results = optimizer.compare_algorithms(
            prepared_graph=prepared_graph,
            start=s_node,
            goal=g_node,
            weight_attr=weight_attr,
            algorithms=["BFS", "DFS", "Greedy", "A*"],
        )
        comp_service = ComparisonService()
        st.session_state.results_dict = results
        st.session_state.comparison_df = comp_service.compare_results(results)
        st.session_state.best_algo = comp_service.get_best_algorithm(
            results,
            metric="total_travel_time" if "time" in weight_attr else "total_distance",
        )
        st.session_state.active_algo = "ALL"
    else:
        # Run single selected algorithm and replace previous route
        result = optimizer.find_route(
            prepared_graph=prepared_graph,
            start=s_node,
            goal=g_node,
            algorithm=algo_choice,
            weight_attr=weight_attr,
        )
        st.session_state.results_dict = {algo_choice: result}
        st.session_state.active_algo = algo_choice
        st.session_state.comparison_df = None
        st.session_state.best_algo = algo_choice


# Check if triggered from sidebar buttons
if controls["clicked_algo"]:
    with st.spinner(f"Calculating {controls['clicked_algo']} route..."):
        execute_algorithm(controls["clicked_algo"])
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# 6. Main Dashboard View
# ─────────────────────────────────────────────────────────────────────────────
render_dashboard_header(
    city=st.session_state.current_city,
    vehicle_type=controls["vehicle_type"],
    start_node=controls["start_node"],
    goal_node=controls["goal_node"],
    traffic_condition=controls["traffic_condition"],
)

graph_for_stats = st.session_state.graph
network_columns = st.columns(4)
with network_columns[0]:
    st.metric("Intersections", f"{graph_for_stats.number_of_nodes():,}")
with network_columns[1]:
    st.metric("Road connections", f"{graph_for_stats.number_of_edges():,}")
with network_columns[2]:
    result_values = [result for result in st.session_state.results_dict.values() if result.found]
    route_distance = result_values[0].total_distance if result_values else None
    st.metric("Route distance", format_distance(route_distance) if route_distance is not None else "—")
with network_columns[3]:
    route_time = result_values[0].total_travel_time if result_values else None
    st.metric("Estimated travel time", format_time(route_time) if route_time is not None else "—")

# ── Interactive Algorithm Action Bar Above the Map ───────────────────────────
st.markdown("#### ⚡ ROUTE COMPUTATION")
col_btn1, col_btn2, col_btn3, col_btn4, col_btn5, col_btn6 = st.columns([1, 1, 1, 1.2, 1.2, 0.8])

with col_btn1:
    if st.button("🔵 Run BFS", use_container_width=True, help="Explore layer-by-layer (Blue line)"):
        with st.spinner("Executing Breadth-First Search locally..."):
            execute_algorithm("BFS")
            st.rerun()

with col_btn2:
    if st.button("🟠 Run DFS", use_container_width=True, help="Explore deep branches (Orange line)"):
        with st.spinner("Executing Depth-First Search locally..."):
            execute_algorithm("DFS")
            st.rerun()

with col_btn3:
    if st.button("🟣 Run Greedy", use_container_width=True, help="Straight-line heuristic search (Purple line)"):
        with st.spinner("Executing Greedy Best-First Search locally..."):
            execute_algorithm("Greedy")
            st.rerun()

with col_btn4:
    if st.button("🟢 Run A* (Optimal)", use_container_width=True, help="Optimal f = g + h pathfinding (Green line)"):
        with st.spinner("Executing A* Search locally..."):
            execute_algorithm("A*")
            st.rerun()

with col_btn5:
    if st.button("📊 Benchmark All", use_container_width=True, help="Compare all 4 algorithms"):
        with st.spinner("Running all 4 algorithms for comparison..."):
            execute_algorithm("ALL")
            st.rerun()

with col_btn6:
    if st.button("🗑️ Reset", use_container_width=True, help="Clear active routes"):
        st.session_state.results_dict = {}
        st.session_state.active_algo = None
        st.session_state.comparison_df = None
        st.rerun()


# ── Section A: Interactive Map (Main Component) ──────────────────────────────
st.markdown("### 🗺️ Interactive City Road Network")

center_coords = get_city_center(st.session_state.current_city)
visualizer = MapVisualizer()

prepared_graph_to_render = getattr(st.session_state, "prepared_graph", st.session_state.graph)

folium_map = visualizer.create_route_map(
    graph=prepared_graph_to_render,
    results_dict=st.session_state.results_dict,
    start_node=controls["start_node"],
    end_node=controls["goal_node"],
    closed_roads=controls["closed_roads"],
    center_lat=center_coords[0],
    center_lon=center_coords[1],
)

render_map(folium_map, height=690)

# Legend Pills
active_name = st.session_state.active_algo if st.session_state.active_algo else "None (Select Algorithm Above)"
st.markdown(
    f"""
    <div style="margin-top: 0.5rem; margin-bottom: 1.25rem; display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem;">
        <span style="font-size: 0.85rem; color: #94a3b8; font-weight: 600;">Active Route Display:</span>
        <span class="algo-pill {'astar' if active_name == 'A*' else 'bfs' if active_name == 'BFS' else 'dfs' if active_name == 'DFS' else 'greedy' if active_name == 'Greedy' else ''}">
            {active_name}
        </span>
        <span style="font-size: 0.75rem; color: #64748b;">|</span>
        <span style="font-size: 0.75rem; color: #3498db;">● BFS: Blue</span>
        <span style="font-size: 0.75rem; color: #e67e22;">● DFS: Orange</span>
        <span style="font-size: 0.75rem; color: #9b59b6;">● Greedy: Purple</span>
        <span style="font-size: 0.75rem; color: #2ecc71;">● A*: Green</span>
        <span style="font-size: 0.75rem; color: #ef4444;">■ Closed Road: Red (Excluded)</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ── Section B: Route Metrics & Telemetry (Updated dynamically) ───────────────
if st.session_state.results_dict:
    # If a single algorithm route is active
    if st.session_state.active_algo and st.session_state.active_algo != "ALL":
        algo_name = st.session_state.active_algo
        res = st.session_state.results_dict.get(algo_name)

        if res and res.found:
            st.markdown(f"#### 📈 {get_algorithm_emoji(algo_name)} {algo_name} Route Telemetry")
            m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)

            with m_col1:
                st.metric("Route Distance", format_distance(res.total_distance))
            with m_col2:
                st.metric("Estimated Travel Time", format_time(res.total_travel_time))
            with m_col3:
                st.metric("Nodes Explored", format_nodes(res.nodes_explored))
            with m_col4:
                st.metric("Execution Latency", format_execution_time(res.execution_time))
            with m_col5:
                st.metric("Edges Traversed", format_nodes(res.edges_traversed))

            # Expandable Node Sequence
            with st.expander(f"🔍 Inspect {algo_name} Node Sequence ({len(res.path)} waypoints)"):
                path_str = " ➔ ".join(str(n) for n in res.path[:60])
                if len(res.path) > 60:
                    path_str += f" ... (+{len(res.path) - 60} more nodes) ➔ {res.path[-1]}"
                st.code(path_str, language="text")
                st.caption(f"Traversed {res.edges_traversed} edges across {res.nodes_explored} explored network vertices.")

        elif res and not res.found:
            st.error(f"❌ No traversable route found using {algo_name}. Destination is unreachable due to road blockades or graph partitions.")

    # If "Benchmark All" was selected
    elif st.session_state.active_algo == "ALL":
        render_comparison(
            results_dict=st.session_state.results_dict,
            comparison_df=st.session_state.comparison_df,
            best_algo_name=st.session_state.best_algo,
        )
        render_statistics(results_dict=st.session_state.results_dict)

else:
    st.info(
        r"👆 **Ready for Route Calculation**: Click any algorithm button above (e.g. **🟢 Run A\*** or **🔵 Run BFS**) "
        "to calculate its route locally in Python and display it directly on the map."
    )
