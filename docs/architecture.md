# System Architecture
## Intelligent Emergency Route Planner | CSE276 AI Foundations

---

## 1. Architectural Overview

The **Intelligent Emergency Route Planner** is designed around a decoupled, modular architecture adhering to the **Model-View-Controller (MVC)** and **Service-Oriented Architecture (SOA)** design principles. The platform bridges real-world geospatial graph data (OpenStreetMap) with classical AI search algorithms, real-time traffic simulations, emergency vehicle priority heuristics, and an interactive dashboard.

```
+-------------------------------------------------------------------+
|                        USER INTERFACE                             |
|               (Streamlit + Custom Dark Navy CSS)                  |
|  - City Selection       - Start/Goal Nodes    - Vehicle Profiles  |
|  - Traffic Slider       - Road Closures       - Algorithm Toggles |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                     APPLICATION CONTROLLER                        |
|                           (app.py)                                |
|  - Session State Mgmt   - Caching Pipeline    - Event Dispatcher  |
+---------------------------------+---------------------------------+
                                  |
        +-------------------------+-------------------------+
        |                                                   |
        v                                                   v
+-------------------------------+   +-------------------------------+
|     GEOSPATIAL DATA LAYER     |   |   TRAFFIC & INCIDENT ENGINE   |
|   (core.graph_builder /       |   |   (simulation.traffic_sim,    |
|    core.graph_loader)         |   |    simulation.road_closures,  |
|  - OSMnx / OpenStreetMap      |   |    simulation.priority)       |
|  - MultiDiGraph Storage       |   |  - Multipliers & Delays       |
|  - Road Geometry + Attributes|   |  - Dynamic Edge Removal       |
|  - Local GraphML / PKL Cache  |   |  - Vehicle Speed Factors      |
+---------------+---------------+   +---------------+---------------+
                |                                   |
                +-----------------+-----------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                     CENTRAL ROUTE OPTIMIZER                       |
|                   (core.route_optimizer.py)                       |
|  - Clones working graph copy (preserves baseline network)         |
|  - Applies traffic weights, closures, and vehicle priority        |
|  - Coordinates benchmark runs across selected AI algorithms       |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                       AI SEARCH ENGINE                            |
|                     (algorithms package)                          |
|  - Breadth-First Search (BFS)       - Depth-First Search (DFS)    |
|  - Greedy Best-First Search         - A* Search (Optimal)         |
|  - Admissible Heuristic Engine (Haversine & Time Lower-Bound)     |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                   ANALYTICS & COMPARISON ENGINE                   |
|                   (services.comparison_service)                   |
|  - Execution Time Benchmark (ms)    - Total Route Distance (m)    |
|  - Nodes & Edges Explored Count     - Estimated Travel Time (s)   |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                    VISUALIZATION ENGINE                           |
|                  (visualization package)                          |
|  - Interactive Folium Geospatial Map with Multi-Route Overlays    |
|  - Dynamic Plotly Comparative Multi-Metric Charts                 |
|  - Detailed Node Sequence Expanders & Diagnostics                 |
+-------------------------------------------------------------------+
```

---

## 2. Component Responsibilities

### 2.1 Web Presentation Layer (`components/` & `assets/`)
- **`app.py`**: Primary entry point. Binds Streamlit reactive events with application services and visualization renderers.
- **`components/sidebar.py`**: Manages collapsible controls, incident coordinates, and parameter validation. The Randomize Coordinates button uses an `on_click` callback to update both keyed dropdowns before the next render.
- **`components/dashboard.py`**: Renders emergency incident cards, active vehicle readiness, and situational telemetry.
- **`components/map_component.py`**: Embeds interactive Folium maps with toggleable algorithm route layers.
- **`components/algorithm_comparison.py`**: Displays multi-metric data tables and Plotly comparison charts.
- **`components/statistics.py`**: Formats individual algorithm performance metrics and node sequence paths.
- **`assets/styles.css`**: Professional dark navy emergency operations center theme.

### 2.2 Geospatial & Graph Engine (`core/`)
- **`graph_builder.py`**: Uses OSMnx to download drivable road graphs, enriches speed and travel-time fields, preserves each edge's LineString coordinates for display, and caches raw GraphML and processed graph data.
- **`graph_loader.py`**: Loads a processed cache first, then downloads real OSM data. Mumbai uses specific-place lookups followed by a configurable center/radius `graph_from_point()` fallback. Download failures produce a user-facing error. A synthetic graph helper exists for development/tests only.
- **`heuristic.py`**: Pure geometric mathematical functions for great-circle distance (Haversine formula) and lower-bound transit times.
- **`cost_calculator.py`**: Edge cost extraction, speed-to-time conversion, and unit normalization.
- **`route_optimizer.py`**: Orchestrates graph preparation and simultaneous algorithm benchmarking without mutating the baseline network.

### 2.3 Traffic & Incident Simulation (`simulation/`)
- **`traffic_simulator.py`**: Overlays dynamic congestion multipliers (`Normal`: 1.0x, `Moderate`: 1.5x, `Heavy`: 2.5x, `Severe`: 4.0x) on edge travel times.
- **`road_closures.py`**: Simulates emergency road blockades, accidents, or bridge collapses by removing specific directed edges from the active routing copy.
- **`emergency_priority.py`**: Adjusts transit times according to vehicle capabilities (`Ambulance`: 1.2x speed factor, `Fire Truck`: 1.1x speed factor, `Rescue Vehicle`: 1.15x speed factor).

### 2.4 Classical AI Search Algorithms (`algorithms/`)
- **`bfs.py`**: Unweighted, FIFO queue-based breadth traversal guaranteeing minimum-hop paths.
- **`dfs.py`**: LIFO stack-based depth traversal demonstrating the hazards of unguided deep exploration in cyclic graphs.
- **`greedy.py`**: Priority queue informed search driven purely by straight-line Haversine distance heuristic $h(n)$.
- **`astar.py`**: Heuristic evaluation using $f(n) = g(n) + h(n)$ with admissible heuristics, ensuring optimal pathfinding for distance and transit time.
- **`algorithm_utils.py`**: Shared `AlgorithmResult` data structures, back-pointer path reconstruction, and path metric calculations.

---

## 3. Data Flow Pipeline

1. **Initialization**: On application load, `graph_loader` checks the processed disk cache. If unavailable, it downloads a real OSM drive network, including the Mumbai point/radius fallback when needed.
2. **User Configuration**: The operator specifies origin/destination nodes, vehicle type, traffic condition, and closed roads in the sidebar. Randomization samples two distinct nodes from the currently available dropdown options.
3. **Graph Preparation**: `RouteOptimizer` creates an isolated working copy of the graph, scales edge weights via `TrafficSimulator`, prunes edges via `RoadClosureManager`, and factors in vehicle speed via `EmergencyPriorityManager`.
4. **Search Execution**: Each chosen algorithm searches the graph independently, recording its visited vertices, frontier expansions, path reconstruction, and runtime metrics using high-precision timers (`time.perf_counter`).
5. **Analytics & Aggregation**: `ComparisonService` collates individual algorithm outputs into a benchmark table and ranks the best-performing route.
6. **Rendering**:
   - `MapVisualizer` rebuilds each node path from edge geometries and draws road-following Folium polylines, start/end markers, and red closure overlays. Closed edges are absent from the prepared route graph.
   - `visualization.charts` renders interactive Plotly bar charts comparing runtime, nodes visited, distance, and transit time.

