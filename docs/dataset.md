# Dataset & Road Network Preprocessing
## OpenStreetMap Ingestion, Graph Modeling & Synthetic Traffic Simulation

---

## 1. Geographic Data Source: OpenStreetMap (OSM)

The primary geographic foundation for this project is **OpenStreetMap (OSM)**, a crowdsourced, open-access collaborative project that maps global infrastructure with high precision.

### 1.1 Data Primitives
OSM represents geospatial infrastructure using three core elements:
1. **Nodes**: Specific geographic points defined by latitude and longitude coordinates in decimal degrees (WGS-84 reference ellipsoid). In our graph, road intersections, endpoints, and sharp turns become NetworkX vertices.
2. **Ways**: Ordered sequences of nodes forming linear features (roads, footpaths, rivers) or enclosed polygons (buildings, parks). In our road network, drivable ways represent directed edges.
3. **Relations**: Groupings of nodes and ways defining complex relationships (e.g., turn restrictions, multi-lane highways).
4. **Tags**: Key-value metadata pairs attached to elements (e.g., `highway=motorway`, `maxspeed=80`, `oneway=yes`, `name=Grafton Street`).

---

## 2. Road Network Ingestion via OSMnx

The Python library **OSMnx** acts as the bridge between OSM's Overpass API and Python's graph representations:
- **Query Type**: Drivable public road network (`network_type='drive'`).
- **Graph Topology**: Simplified directed multi-graph (`networkx.MultiDiGraph`), retaining parallel edges, one-way constraints, and each road edge's geographic LineString geometry.
- **Geographic Coverage**: Supported preset urban environments including Dublin, Cork, Galway, Limerick, London, Manhattan, and Mumbai.

---

## 3. Preprocessing Pipeline

When raw OSM data is ingested, the system applies a structured transformation pipeline:

```
[Raw Overpass XML / JSON]
           |
           v
[OSMnx MultiDiGraph Construction]
           |
           v
[Topology Simplification] (Removes non-intersection nodes while preserving length)
           |
           v
[Speed Limit Imputation] (Extracts 'maxspeed' tag or maps road class to default speed)
           |
           v
[Free-Flow Travel Time Computation] (travel_time = length / speed)
           |
           v
[Disk Caching] (Raw: data/raw/*.graphml | Processed: data/processed/*.pkl)
```

### 3.1 Speed Imputation Defaults
When roads lack explicit `maxspeed` tags in OSM, the system applies conservative urban defaults:
- `motorway`: 120 km/h
- `trunk`: 100 km/h
- `primary`: 80 km/h
- `secondary`: 60 km/h
- `tertiary`: 50 km/h
- `residential`: 30 km/h
- `service`: 20 km/h
- `unclassified`: 40 km/h

---

## 4. Mumbai Geocoding and Download Fallback

Nominatim may return Mumbai as a point rather than a city-boundary polygon, so `graph_from_place("Mumbai, India")` can fail. `core/graph_builder.py` first tries `Mumbai, Maharashtra, India`, then `Mumbai, India`. If both place lookups fail or return unsuitable geometries, OSMnx downloads the real drivable network with `graph_from_point()` around the configured Mumbai center. The radius defaults to 12,000 m and can be changed with `MUMBAI_GRAPH_RADIUS_METERS`.

Graphs are cached locally under `data/raw/` and `data/processed/`. If both geocoding and point-based download fail, the loader raises a useful error; it does not substitute generated coordinates for Mumbai's real road network. `create_fallback_graph()` remains available as a synthetic development/test fixture and must not be interpreted as OSM data.

## 5. Road Geometry and Route Rendering

OSMnx edge geometries are converted into ordered latitude/longitude coordinate sequences (`geometry_coords`) during graph enrichment and preserved in the processed graph cache. Each calculated node path is reconstructed by concatenating the geometry of its directed edges. Folium draws those coordinates as polylines, retaining street bends and curves from the source geometry. Endpoint coordinates are used only when an edge has no geometry. Closed roads are removed from the prepared graph used for route calculation; the map renders closure overlays using the original graph's edge geometry.

---

## 6. Traffic Congestion & Delay Modeling

Traffic congestion is simulated as a dynamic scaling factor applied to baseline free-flow travel times:

$$t_{\text{traffic}} = t_{\text{base}} \times \mu_{\text{congestion}}$$

Where $\mu_{\text{congestion}}$ varies by condition level:
- **Normal**: $\mu = 1.0$ (Free flow, 0% delay)
- **Moderate**: $\mu = 1.5$ (Moderate congestion, +50% delay)
- **Heavy**: $\mu = 2.5$ (Peak hour congestion, +150% delay)
- **Severe**: $\mu = 4.0$ (Severe gridlock, +300% delay)

A fixed pseudo-random seed (`config.TRAFFIC_RANDOM_SEED = 42`) guarantees exact reproducibility across repeated algorithm benchmarks.

---

## 7. Licensing & Attribution
- OpenStreetMap data is licensed under the **Open Database License (ODbL)** by the OpenStreetMap Foundation (OSMF).
- CartoDB dark-themed map tiles are provided by Carto and OpenStreetMap contributors.

