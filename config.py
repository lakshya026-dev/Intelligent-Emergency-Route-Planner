"""
Configuration settings for the Intelligent Emergency Route Planner.

Centralizes all application constants, default values, and configuration
parameters used across modules.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

# ──────────────────────────────────────────────
# CARTO Basemaps API Configuration
# ──────────────────────────────────────────────
CARTO_API_KEY = os.getenv("CARTO_API_KEY", "").strip()

# CARTO Dark Matter Tile URL (includes ?key= parameter when provided)
if CARTO_API_KEY:
    MAP_TILE_STYLE = f"https://basemaps.cartocdn.com/rastertiles/dark_all/{{z}}/{{x}}/{{y}}.png?key={CARTO_API_KEY}"
else:
    MAP_TILE_STYLE = "cartodbdark_matter"

MAP_TILE_ATTR = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'


# ──────────────────────────────────────────────
# Directory Paths
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
ASSETS_DIR = BASE_DIR / "assets"

# ──────────────────────────────────────────────
# Default City / Area Settings
# ──────────────────────────────────────────────
DEFAULT_CITY = "Dublin, Ireland"
SUPPORTED_CITIES = {
    "Dublin, Ireland": {"center": (53.3498, -6.2603), "zoom": 13},
    "Cork, Ireland": {"center": (51.8985, -8.4756), "zoom": 13},
    "Galway, Ireland": {"center": (53.2707, -9.0568), "zoom": 14},
    "Limerick, Ireland": {"center": (52.6638, -8.6267), "zoom": 14},
    "Mumbai, India": {"center": (19.0760, 72.8777), "zoom": 13},
    "Manhattan, New York": {"center": (40.7831, -73.9712), "zoom": 13},
    "London, England": {"center": (51.5074, -0.1278), "zoom": 13},
}

# ──────────────────────────────────────────────
# Graph / Network Settings
# ──────────────────────────────────────────────
NETWORK_TYPE = "drive"           # OSMnx network type for drivable roads
GRAPH_CACHE_ENABLED = True       # Cache downloaded graphs locally
GRAPH_SIMPLIFY = True            # Simplify graph topology

# ──────────────────────────────────────────────
# Algorithm Colors (for map / charts)
# ──────────────────────────────────────────────
ALGORITHM_COLORS = {
    "BFS": "#3498db",        # Blue
    "DFS": "#e67e22",        # Orange
    "Greedy": "#9b59b6",     # Purple
    "A*": "#2ecc71",         # Green
}

CLOSED_ROAD_COLOR = "#e74c3c"  # Red

# ──────────────────────────────────────────────
# Traffic Simulation Settings
# ──────────────────────────────────────────────
TRAFFIC_CONDITIONS = {
    "Normal": {"multiplier": 1.0, "color": "#2ecc71", "description": "Free-flowing traffic"},
    "Moderate": {"multiplier": 1.5, "color": "#f39c12", "description": "Some slowdowns expected"},
    "Heavy": {"multiplier": 2.5, "color": "#e67e22", "description": "Significant delays"},
    "Severe": {"multiplier": 4.0, "color": "#e74c3c", "description": "Major congestion, avoid if possible"},
}

TRAFFIC_RANDOM_SEED = 42  # Fixed seed for reproducible traffic generation

# ──────────────────────────────────────────────
# Emergency Vehicle Configuration
# ──────────────────────────────────────────────
EMERGENCY_VEHICLES = {
    "Ambulance": {
        "icon": "🚑",
        "priority": 1,          # Highest priority
        "speed_factor": 1.2,    # Can move faster due to sirens / right-of-way
        "color": "#e74c3c",
        "description": "Medical emergency — time-critical patient transport",
    },
    "Fire Truck": {
        "icon": "🚒",
        "priority": 2,
        "speed_factor": 1.1,
        "color": "#e67e22",
        "description": "Fire response — heavy vehicle, needs wider roads",
    },
    "Rescue Vehicle": {
        "icon": "🚐",
        "priority": 3,
        "speed_factor": 1.15,
        "color": "#3498db",
        "description": "Search and rescue operations",
    },
}

# ──────────────────────────────────────────────
# Optimization Objectives
# ──────────────────────────────────────────────
OPTIMIZATION_OBJECTIVES = {
    "Minimum Distance": {
        "weight_attr": "length",
        "description": "Shortest physical distance (meters)",
        "unit": "m",
    },
    "Minimum Travel Time": {
        "weight_attr": "travel_time",
        "description": "Fastest route based on speed limits",
        "unit": "s",
    },
    "Traffic-Aware Travel Time": {
        "weight_attr": "traffic_travel_time",
        "description": "Fastest route considering current traffic",
        "unit": "s",
    },
}

# ──────────────────────────────────────────────
# Speed Defaults (km/h) — used when OSM data
# does not include maxspeed tags
# ──────────────────────────────────────────────
DEFAULT_SPEEDS = {
    "motorway": 120,
    "trunk": 100,
    "primary": 80,
    "secondary": 60,
    "tertiary": 50,
    "residential": 30,
    "service": 20,
    "unclassified": 40,
    "default": 40,
}

# ──────────────────────────────────────────────
# Map Display Settings
# ──────────────────────────────────────────────
MAP_DEFAULT_ZOOM = 13
MAP_ROUTE_WEIGHT = 5                   # Line weight for route paths
MAP_ROUTE_OPACITY = 0.85

# ──────────────────────────────────────────────
# UI / Dashboard Theme
# ──────────────────────────────────────────────
DASHBOARD_TITLE = "Intelligent Emergency Route Planner"
DASHBOARD_SUBTITLE = "AI-Powered Emergency Vehicle Routing System"
DASHBOARD_ICON = "🚨"

# ──────────────────────────────────────────────
# Fallback Sample Graph
# ──────────────────────────────────────────────
USE_FALLBACK_IF_OFFLINE = True  # Auto-fallback to sample graph when OSM is unreachable

