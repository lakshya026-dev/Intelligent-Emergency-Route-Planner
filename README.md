# 🚨 Intelligent Emergency Route Planner (IERP)
### CSE276 – Artificial Intelligence Foundations | Continuous Assessment 1 (CA2) Project

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-red.svg)](https://streamlit.io/)
[![Mapping](https://img.shields.io/badge/GIS-OSMnx%20%7C%20Folium-green.svg)](https://osmnx.readthedocs.io/)
[![Tests](https://img.shields.io/badge/Tests-31%20Passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent, AI-powered geospatial routing and simulation web application designed to identify optimal emergency response routes across real-world urban road networks. The system implements and benchmarks four classical Artificial Intelligence search algorithms (**Breadth-First Search**, **Depth-First Search**, **Greedy Best-First Search**, and **A\* Search**) under dynamic traffic conditions, road blockades, and emergency vehicle priorities.

---

## 📌 1. Project Introduction & Problem Statement

In life-or-death emergency scenarios—such as patient cardiac arrest, active structural fires, or tactical search and rescue—every second saved en route directly impacts survival outcomes. Modern urban environments present complex navigation challenges:
- Real-world road networks feature varying street classes and speed limits.
- Traffic congestion dynamically fluctuates throughout the day.
- Unforeseen road closures, accidents, or bridge blockades require immediate detours.
- Different emergency units (Ambulances vs. Fire Trucks) require distinct speed factors.

This project delivers a **fully functional, interactive emergency operations center dashboard** that solves this problem using fundamental AI search techniques implemented from scratch in pure Python without black-box routing APIs.

---

## ✨ 2. Key Features

- **🧠 4 Classical AI Search Algorithms (Implemented from Scratch)**:
  - **Breadth-First Search (BFS)**: Unweighted layer-by-layer exploration guaranteeing minimum network hops (drawn in **Blue**).
  - **Depth-First Search (DFS)**: Deep branch exploration demonstrating unguided search pitfalls (drawn in **Orange**).
  - **Greedy Best-First Search**: Heuristic-guided search using straight-line Haversine distance $f(n) = h(n)$ (drawn in **Purple**).
  - **A\* Search**: Optimal informed search using $f(n) = g(n) + h(n)$ with mathematically admissible heuristics (drawn in **Green**).
- **🗺️ Interactive Map Centerpiece (Visible & Active at All Times)**:
  - Drivable street graph extraction via OpenStreetMap and OSMnx, preserving road-edge geometry so route lines follow actual streets.
  - One-click algorithm execution buttons (`🔵 BFS`, `🟠 DFS`, `🟣 Greedy`, `🟢 A*`).
  - **Dynamic Route Replacement**: Clicking another algorithm immediately clears the old route and renders the newly calculated route in its designated color.
  - Interactive panning, zooming, and waypoint inspection.
- **📈 Real-Time Live Telemetry Dashboard**:
  - Dynamically displays **Route Distance** (meters & km), **Estimated Travel Time** (seconds & minutes), **Execution Latency** (ms), and **Nodes Explored** (plus edges traversed).
- **🚦 Live Traffic Congestion Simulation**:
  - User-configurable traffic levels (`Normal` 1.0x, `Moderate` 1.5x, `Heavy` 2.5x, `Severe` 4.0x) with reproducible random seeds.
- **🚧 Dynamic Road Blockades & Closures**:
  - Interactively close specific road segments (drawn as red dashed lines on the map).
  - Search algorithms automatically detour around blocked segments.
- **🚑 Emergency Vehicle Priority Modeling**:
  - Configurable profiles for **Ambulance**, **Fire Truck**, and **Rescue Vehicle** with siren speed factors.
- **🌐 Offline Resilience (Zero API Keys Needed)**:
  - Automatic local disk caching (`data/raw/` and `data/processed/`) avoids repeated downloads.
  - Network failures are surfaced clearly instead of showing generated coordinates as real roads.
- **📍 Route Coordinate Controls**: Randomize Coordinates uses a Streamlit callback to select two distinct valid nodes from the current dropdown options.
- **📊 Operations dashboard**: Responsive dark navy presentation, graph-based network statistics, route telemetry, comparison charts, and traffic status indicators.
- **🌆 Mumbai download fallback**: Tries `Mumbai, Maharashtra, India`, then `Mumbai, India`, then uses OSMnx `graph_from_point()` around the configured center. Set `MUMBAI_GRAPH_RADIUS_METERS` to change the default 12,000 m radius.

---

## 💻 3. System Requirements & Prerequisites

Before installing and running the project locally, ensure your machine satisfies:

| Component | Minimum Requirement | Recommended |
|---|---|---|
| **Operating System** | Windows 10/11, macOS 12+, or Ubuntu 20.04+ | Windows 11 / macOS Sonoma / Linux |
| **Python Version** | Python 3.12.0 or newer | Python 3.12.x |
| **RAM** | 4 GB | 8 GB or more (for caching large city networks) |
| **Storage** | 500 MB free space | 1 GB free space |
| **Web Browser** | Chrome, Edge, Firefox, or Brave | Modern Chromium-based browser |
| **Internet** | Only required during first city download | Offline mode supported out of the box |

---

## 🛠️ 4. Technology Stack

| Category | Technologies |
|---|---|
| **Programming Language** | Python 3.12+ |
| **Web Dashboard** | Streamlit, Custom Dark Navy CSS, HTML5 |
| **Geospatial & Networks**| OpenStreetMap, OSMnx, NetworkX, GeoPandas, Shapely |
| **Interactive Maps** | Folium, Streamlit-Folium |
| **Data Processing** | Pandas, NumPy, PyArrow |
| **Visualization** | Plotly Graph Objects / Express, Matplotlib |
| **Testing & Quality** | Pytest, Python standard `unittest` |

---

## 📁 5. Project Directory Structure

```
intelligent-emergency-route-planner/
│
├── app.py                     # Master Streamlit Operations Dashboard
├── config.py                  # Central configuration and system constants
├── requirements.txt           # Package dependencies
├── README.md                  # Comprehensive documentation
├── .gitignore                 # Version control exclusions
├── .env.example               # Environment variable template
│
├── .vscode/
│   ├── launch.json            # VS Code F5 debugging & launch profiles
│   └── settings.json          # VS Code Python test configuration
│
├── assets/
│   └── styles.css             # Dark navy emergency operations center theme
│
├── data/
│   ├── raw/                   # Cached raw OSM GraphML files
│   ├── processed/             # Cached enriched network pickles
│   └── sample/
│       └── sample_traffic.csv # Baseline traffic distribution dataset
│
├── algorithms/
│   ├── __init__.py
│   ├── bfs.py                 # Breadth-First Search (FIFO queue)
│   ├── dfs.py                 # Depth-First Search (LIFO stack)
│   ├── greedy.py              # Greedy Best-First Search (Heapq priority queue)
│   ├── astar.py               # A* Optimal Search (g + h evaluation)
│   └── algorithm_utils.py     # Result dataclasses & path metric helpers
│
├── core/
│   ├── __init__.py
│   ├── simple_graph.py        # Lightweight transparent MultiDiGraph fallback
│   ├── graph_builder.py       # OSMnx road network ingestion & attribute enrichment
│   ├── graph_loader.py        # Cached graph loader and development sample graph helper
│   ├── route_optimizer.py     # Central multi-algorithm dispatch & simulation orchestrator
│   ├── heuristic.py           # Admissible Haversine & lower-bound time heuristics
│   └── cost_calculator.py     # Edge cost retrieval & speed-to-time conversion
│
├── simulation/
│   ├── __init__.py
│   ├── traffic_simulator.py   # Congestion multipliers & traffic distributions
│   ├── road_closures.py       # Incident blockade tracking & edge removal
│   └── emergency_priority.py  # Vehicle profiles & priority speed factor scaling
│
├── services/
│   ├── __init__.py
│   ├── map_service.py         # City coordinates & graph access service
│   ├── location_service.py    # Node dropdown options and callback-based random endpoints
│   └── comparison_service.py  # Tabular analytics & optimal route selection
│
├── visualization/
│   ├── __init__.py
│   ├── map_visualizer.py      # Folium map creator with multi-layer route overlays
│   ├── charts.py              # Interactive Plotly comparative benchmark charts
│   └── metrics.py             # Human-readable formatting & emoji helpers
│
├── components/
│   ├── __init__.py
│   ├── sidebar.py             # Sidebar controls & parameter inputs
│   ├── dashboard.py           # Incident header cards & status telemetry
│   ├── map_component.py       # Embedded Folium map wrapper with HTML fallback
│   ├── algorithm_comparison.py# Comparison tables & multi-tab charts
│   └── statistics.py          # Metric summary cards & node waypoint inspect
│
├── tests/
│   ├── test_bfs.py            # Unit tests for BFS
│   ├── test_dfs.py            # Unit tests for DFS
│   ├── test_greedy.py         # Unit tests for Greedy Best-First Search
│   ├── test_astar.py          # Unit tests for A* optimality
│   ├── test_traffic.py        # Unit tests for traffic & closures
│   ├── test_graph.py          # Unit tests for graph structure & heuristics
│   ├── test_route_optimizer.py# Unit tests for route optimizer service
│   └── test_random_coordinates.py # Random coordinate callback tests
│
└── docs/
    ├── architecture.md        # Comprehensive system architecture & data flow
    ├── algorithms.md          # Theoretical analysis, complexity & pseudocode
    ├── dataset.md             # OpenStreetMap pipeline & preprocessing guide
    └── project_report.md      # Complete Continuous Assessment (CA1) report
```

---

## 🚀 6. Step-by-Step Local Installation Guide

Follow these steps to set up the project on your local machine:

### Step 1: Open Terminal in Project Directory
Open your terminal (PowerShell, Command Prompt, or Bash) and navigate to the project directory:
```bash
cd "L:\Projects\Intelligent Emergency Route Planner (CSE-276)"
```

### Step 2: Create a Virtual Environment (Recommended)
Creating an isolated virtual environment prevents library version conflicts:

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell displays an execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and then run the activate command again).*

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Upgrade pip and Install Dependencies
Install all required packages from `requirements.txt`:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> **Dependency compatibility**: Use the pinned versions in `requirements.txt`. The comparison table is rendered from live results without Streamlit's Arrow-backed `st.dataframe`, avoiding PyArrow/NumPy ABI mismatches.

### Step 4: Verify Installation
Verify that all core modules import cleanly by running:
```bash
python -c "from algorithms.bfs import bfs_search; from algorithms.astar import astar_search; from core.graph_loader import create_fallback_graph; print('✅ All modules imported successfully!')"
```

---

## 🖥️ 7. How to Run Locally on Your System

### Method 1: Run via Command Line (CLI)
From the project root directory with your virtual environment active, run:
```bash
streamlit run app.py
```

The Streamlit web server will start and automatically open the application in your default browser at:
```
Local URL: http://localhost:8501
```

To run on a specific custom port:
```bash
streamlit run app.py --server.port 8080
```

---

### Method 2: One-Click Run in Visual Studio Code (<kbd>F5</kbd>)

The repository includes a ready-to-use [.vscode/launch.json](file:///.vscode/launch.json) profile:

1. Open the project folder in **Visual Studio Code**.
2. Press <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>D</kbd> (or click the **Run and Debug** icon on the left bar).
3. Select **`🚨 Run Streamlit Dashboard`** from the configuration dropdown at the top.
4. Press <kbd>F5</kbd> (or click the green **Play ▶** button).
5. The integrated terminal will launch the Streamlit server and open your browser automatically.

---

## 🎛️ 8. Interactive Dashboard Walkthrough

```
+-----------------------------------------------------------------------------------+
|  🚨 INTELLIGENT EMERGENCY ROUTE PLANNER | INCIDENT COMMAND CENTER                 |
|  [Ambulance: Priority 1]  [Origin: Node 0]  [Target: Node 80]  [Congestion: Heavy]|
+-----------------------------------------------------------------------------------+
|  ⚡ AI Route Pathfinding:                                                         |
|  [ 🔵 Run BFS ]  [ 🟠 Run DFS ]  [ 🟣 Run Greedy ]  [ 🟢 Run A* ]  [ 📊 Benchmark]|
+-----------------------------------------------------------------------------------+
|                                                                                   |
|                      INTERACTIVE GEOSPATIAL MAP (FOLIUM)                          |
|                    - Green Marker: Dispatch Station (Start)                       |
|                    - Red Marker: Emergency Incident (Goal)                        |
|                    - Active Route: Rendered in Algorithm's Color                  |
|                    - Red Dashed Segments: Closed Road Blockades                   |
|                                                                                   |
+-----------------------------------------------------------------------------------+
|  📈 LIVE ROUTE TELEMETRY:                                                         |
|  Distance: 4,585 m | Travel Time: 8 min 47 sec | Latency: 0.28 ms | Nodes: 81     |
+-----------------------------------------------------------------------------------+
```

### Typical Operational Workflow:
1. **Select Coordinates**: Choose origin and destination nodes in the sidebar, or click `🎲 Randomize Coordinates`. It chooses two distinct nodes from the visible dropdown options and is disabled when fewer than two are available.
2. **Configure Conditions**:
   - Choose vehicle profile (**Ambulance**, **Fire Truck**, or **Rescue Vehicle**).
   - Set traffic congestion (**Normal**, **Moderate**, **Heavy**, **Severe**).
   - Enable **Road Blockades** and select segments to close (shown in **Red**).
3. **Execute Any Search Algorithm**:
   - Click **`🔵 Run BFS`**: Evaluates layer-by-layer and draws the **Blue** route.
   - Click **`🟢 Run A*`**: Automatically removes the previous route and draws the **Green** optimal route.
   - Click **`🟣 Run Greedy`**: Displays the straight-line heuristic **Purple** route.
   - Click **`🟠 Run DFS`**: Displays the deep-branch **Orange** route.
4. **Compare All Algorithms**:
   - Click **`📊 Benchmark All`** to calculate all 4 algorithms simultaneously and view comparative Plotly charts and tables.

---

## 🧪 9. Running the Automated Test Suite

The project includes **31 unit tests** across 8 test modules:

### Run via Standard Python `unittest` (No extra dependencies needed):
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Run via `pytest`:
```bash
pytest tests/ -v
```

### Expected Output:
```text
test_distance_optimality (test_astar.TestAStar.test_distance_optimality) ... ok
test_invalid_nodes (test_astar.TestAStar.test_invalid_nodes) ... ok
test_start_equals_goal (test_astar.TestAStar.test_start_equals_goal) ... ok
test_time_objective (test_astar.TestAStar.test_time_objective) ... ok
test_valid_optimal_path (test_astar.TestAStar.test_valid_optimal_path) ... ok
test_invalid_goal_node (test_bfs.TestBFS.test_invalid_goal_node) ... ok
test_invalid_start_node (test_bfs.TestBFS.test_invalid_start_node) ... ok
test_start_equals_goal (test_bfs.TestBFS.test_start_equals_goal) ... ok
test_unreachable_node (test_bfs.TestBFS.test_unreachable_node) ... ok
test_valid_path_found (test_bfs.TestBFS.test_valid_path_found) ... ok
test_cyclic_graph_handling (test_dfs.TestDFS.test_cyclic_graph_handling) ... ok
test_invalid_nodes (test_dfs.TestDFS.test_invalid_nodes) ... ok
test_start_equals_goal (test_dfs.TestDFS.test_start_equals_goal) ... ok
test_valid_path_found (test_dfs.TestDFS.test_valid_path_found) ... ok
test_cost_calculator (test_graph.TestGraph.test_cost_calculator) ... ok
test_edge_attributes (test_graph.TestGraph.test_edge_attributes) ... ok
test_haversine_formula (test_graph.TestGraph.test_haversine_formula) ... ok
test_node_attributes (test_graph.TestGraph.test_node_attributes) ... ok
test_heuristic_efficiency (test_greedy.TestGreedy.test_heuristic_efficiency) ... ok
test_invalid_nodes (test_greedy.TestGreedy.test_invalid_nodes) ... ok
test_start_equals_goal (test_greedy.TestGreedy.test_start_equals_goal) ... ok
test_valid_path_found (test_greedy.TestGreedy.test_valid_path_found) ... ok
test_compare_all_algorithms (test_route_optimizer.TestRouteOptimizer.test_compare_all_algorithms) ... ok
test_comparison_service (test_route_optimizer.TestRouteOptimizer.test_comparison_service) ... ok
test_unreachable_due_to_closures (test_route_optimizer.TestRouteOptimizer.test_unreachable_due_to_closures) ... ok
test_emergency_vehicle_speed_factor (test_traffic.TestTrafficSimulation.test_emergency_vehicle_speed_factor) ... ok
test_road_closures (test_traffic.TestTrafficSimulation.test_road_closures) ... ok
test_uniform_traffic_multipliers (test_traffic.TestTrafficSimulation.test_uniform_traffic_multipliers) ... ok

----------------------------------------------------------------------
Ran 31 tests

OK
```

---

## 🔬 10. Algorithmic Theoretical Comparison

| Algorithm | Color on Map | Search Strategy | Complete? | Optimal? | Time Complexity | Space Complexity | Best Use Case |
|---|---|---|---|---|---|---|---|
| **BFS** | **Blue** (`#3498db`) | FIFO Queue (Layers) | Yes | Yes (Unweighted) | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | Minimum-hop paths on unweighted graphs |
| **DFS** | **Orange** (`#e67e22`) | LIFO Stack (Deep Branch) | Yes (Finite) | No | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ | Maze exploration, cycle detection |
| **Greedy** | **Purple** (`#9b59b6`) | Min-Heap ($f = h$) | Yes (Finite) | No | $\mathcal{O}(E \log V)$ | $\mathcal{O}(V)$ | Fast heuristic exploration |
| **A\*** | **Green** (`#2ecc71`) | Min-Heap ($f = g + h$) | Yes | **Yes (Optimal)** | $\mathcal{O}(E \log V)$ | $\mathcal{O}(V)$ | Optimal pathfinding on weighted graphs |

Benchmark values depend on the loaded OSM graph, selected endpoints, traffic, and closures. Use **Benchmark All** in the dashboard to generate current measurements; the table and charts are populated from those live results.

---

## ⚠️ 11. Troubleshooting & FAQs

### Q1: `ImportError: pyarrow requires NumPy 2.0 or newer`
**Cause and fix**: This can happen when the installed PyArrow wheel expects NumPy 2 while the environment uses NumPy 1.x. The comparison table avoids Streamlit's Arrow-backed dataframe widget; keep dependencies aligned with `requirements.txt`. The Folium map also has an HTML rendering fallback if `streamlit-folium` is unavailable.

### Q2: Can the project run completely offline?
The app uses downloaded or locally cached OSM road data. If graph loading and download fail, it displays an actionable error. `create_fallback_graph()` remains available as a development/test helper and is not substituted for real city data in the dashboard.

### Q3: Why does Randomize Coordinates report a session-state exception?
**Cause and fix**: Streamlit does not allow a widget's keyed value to be changed after that widget is created in the current run. Randomize Coordinates uses an `on_click` callback to update both keys before the next render and samples distinct nodes from the visible dropdown options.

### Q4: Why does A* choose a longer distance path when optimizing for travel time?
In real road networks, faster road classes can make a longer-distance route faster overall. Under a travel-time objective, A* minimizes estimated travel time rather than physical distance.

---

## 📚 12. Academic Documentation Links

For comprehensive grading review, refer to the detailed reports in the `docs/` folder:
- **[docs/project_report.md](docs/project_report.md)**: Full Continuous Assessment (CA1) formal report with abstract, methodology, results, and conclusion.
- **[docs/algorithms.md](docs/algorithms.md)**: Mathematical proofs, pseudocode, heuristic admissibility formulas, and asymptotic complexity analysis.
- **[docs/architecture.md](docs/architecture.md)**: System design diagrams, data flow pipelines, and component responsibilities.
- **[docs/dataset.md](docs/dataset.md)**: OpenStreetMap ingestion, speed limit imputation, and synthetic traffic generation model.

---

## 📜 13. License & Credits

- **License**: MIT Open Source License
- **Geographic Data**: © [OpenStreetMap](https://www.openstreetmap.org/) contributors (ODbL License).
- **Course**: CSE276 – Artificial Intelligence Foundations.
