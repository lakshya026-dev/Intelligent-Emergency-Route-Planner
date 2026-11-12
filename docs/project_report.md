# Continuous Assessment Project Report (CA2)
# Intelligent Emergency Route Planner: Multi-Algorithm Geospatial Pathfinding Benchmark

**Course**: CSE276 – Artificial Intelligence Foundations  
**Academic Term**: Continuous Assessment 2 (CA2)  
**System Name**: Intelligent Emergency Route Planner (IERP)  

---

## Abstract
Emergency response vehicles such as ambulances, fire trucks, and rescue squads require rapid, reliable navigation through complex urban road networks. Route planning in dynamic urban settings is complicated by varying speed limits, real-time traffic congestion, road construction, and unexpected physical blockades. This project presents the design, architectural implementation, and empirical evaluation of an **Intelligent Emergency Route Planner**. The system integrates OpenStreetMap road networks via OSMnx, dynamic traffic modeling, road closure simulations, and emergency priority heuristics. Four classical Artificial Intelligence search algorithms—Breadth-First Search (BFS), Depth-First Search (DFS), Greedy Best-First Search, and A* Search—are implemented from scratch without black-box graph solvers. Benchmarks across multiple urban scenarios demonstrate that A* Search with admissible straight-line Haversine and lower-bound travel-time heuristics consistently achieves mathematical optimality while expanding significantly fewer nodes than uninformed methods.

---

## 1. Introduction & Background
In time-critical emergency incidents, reducing response time by mere minutes can save human lives and mitigate structural damages. Classical Dijkstra and uninformed searches are widely understood in theoretical computer science, but practical urban deployments face unique challenges:
1. Physical road distance does not directly correspond to travel duration due to differing speed limits and street hierarchies.
2. Congestion dynamically alters transit times throughout the day.
3. Road incidents and debris require instantaneous detour calculations without full graph re-indexing.

This project investigates how classical AI graph traversal and heuristic search algorithms perform when subjected to realistic geographic constraints and emergency dispatch demands.

---

## 2. Problem Statement
Given a directed road graph $G = (V, E)$, an origin node $s \in V$, a destination incident node $g \in V$, edge cost weights $w(u, v)$ (distance, baseline time, or traffic-adjusted time), and a subset of temporarily impassable edges $E_{\text{closed}} \subset E$, find a path $P = (v_0, v_1, \dots, v_k)$ where $v_0 = s$ and $v_k = g$ such that:

$$\min \sum_{i=0}^{k-1} w(v_i, v_{i+1}) \quad \text{subject to } (v_i, v_{i+1}) \notin E_{\text{closed}}$$

Additionally, the system must evaluate and compare the computational overhead (nodes explored, edges traversed, execution latency) of BFS, DFS, Greedy Best-First, and A* Search.

---

## 3. Project Objectives
1. Implement pure, custom Python implementations of BFS, DFS, Greedy Best-First, and A* without leveraging NetworkX shortest-path library functions.
2. Ingest real-world drivable road networks from OpenStreetMap using OSMnx, enriched with speed limits and transit times.
3. Cache downloaded road graphs locally and handle geocoding/download failures with useful diagnostics, including a point/radius fallback for Mumbai.
4. Model dynamic traffic congestion states and user-configurable road closure blockades.
5. Provide configurable emergency vehicle profiles (Ambulance, Fire Truck, Rescue Vehicle) with specialized speed factors.
6. Present findings through a responsive Streamlit operations dashboard featuring interactive Folium maps and Plotly analytical charts.

---

## 4. Methodology & Implementation
The application is structured into decoupled modules:
- **`core/`**: Graph acquisition, caching, Haversine distance heuristics, and central route optimization.
- **`algorithms/`**: Manual queue/stack/heap implementations of BFS, DFS, Greedy, and A*.
- **`simulation/`**: Traffic multipliers, edge removal for road blockades, and vehicle speed factor scaling.
- **`services/`**: Location parsing, node options, and tabular comparison generation.
- **`visualization/`**: Folium map generation with color-coded multi-route polyline overlays and Plotly visual benchmarks.
- **`components/`**: Streamlit sidebar, incident telemetry header, comparison views, and detailed node sequence expanders.
- **Road geometry**: OSMnx edge LineStrings are retained as ordered coordinates, then concatenated along algorithm node paths for street-following map overlays.
- **Coordinate randomization**: A Streamlit button callback selects distinct nodes from the dropdown's current graph options without mutating widget state after render.

---

## 5. Experimental Results & Performance Benchmark

Benchmark results depend on the loaded graph, origin/destination, objective, traffic setting, and closures. The dashboard's **Benchmark All** action calculates and displays current measurements for all four algorithms. Fixed sample measurements are omitted here so they are not mistaken for reproducible results across different graphs and runtime environments.

---

## 6. Analysis & Discussion
1. **BFS (Uninformed)**: Guarantees the fewest edge hops. However, because edge distances and speed limits vary substantially across real roads, fewer hops do not equate to shorter travel times or distances.
2. **DFS (Uninformed)**: Finds a path on finite reachable graphs but is not cost-optimal; exact exploration and route metrics depend on graph ordering and selected endpoints.
3. **Greedy Best-First (Informed)**: Uses estimated remaining distance and ignores accumulated route cost, so it may return a non-optimal route.
4. **A\* Search (Informed)**: Combines accumulated cost and a lower-bound heuristic; with the configured admissible heuristic and consistent edge costs, it finds an optimal path for the selected weight objective.

---

## 7. Conclusion & Future Scope
The Intelligent Emergency Route Planner fulfills all academic requirements of the CSE276 Artificial Intelligence Foundations syllabus. It demonstrates the critical differences between blind and heuristic searches in real-world spatial environments.

### Future Scope
- **Real-Time Sensor Integration**: Connect live GPS feeds from city transit APIs (e.g., TomTom or Google Traffic).
- **Multi-Vehicle Fleet Routing**: Expand from single-agent dispatch to multi-agent collision avoidance and coordinated hospital routing.
- **Dynamic Re-Routing**: Ingest in-flight telemetry updates to trigger mid-route path re-computation when new accidents occur.

---

## 8. References
1. Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson.
2. Boeing, G. (2017). OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks. *Computers, Environment and Urban Systems*, 65, 126–139.
3. Hart, P. E., Nilsson, N. J., & Raphael, B. (1968). A formal basis for the heuristic determination of minimum cost paths. *IEEE Transactions on Systems Science and Cybernetics*, 4(2), 100–107.
