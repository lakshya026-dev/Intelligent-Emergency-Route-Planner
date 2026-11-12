"""
Map-related services.

Provides helper functions for loading city graphs, listing available
cities, and retrieving city center coordinates.
"""

import logging

import config
from core import graph_loader

logger = logging.getLogger(__name__)


def get_city_graph(city_name):
    """
    Load the road-network graph for *city_name*.

    Attempts to load from cache / OSM via :mod:`core.graph_loader`.
    On any failure, falls back to a synthetic fallback graph so the
    application can still function offline.

    Args:
        city_name: A key from ``config.SUPPORTED_CITIES``
                   (e.g. ``"Dublin, Ireland"``).

    Returns:
        A NetworkX MultiDiGraph representing the road network.
    """
    try:
        graph = graph_loader.load_graph(city_name)
        if graph is not None:
            logger.info("Loaded graph for '%s' (%d nodes).", city_name, len(graph.nodes))
            return graph
    except Exception as exc:
        logger.warning("Failed to load graph for '%s': %s", city_name, exc)

    # Fallback
    logger.info("Using fallback graph for '%s'.", city_name)
    return graph_loader.create_fallback_graph(city_name=city_name)


def get_available_cities():
    """
    Return a list of supported city names.

    Returns:
        list[str]: City names from ``config.SUPPORTED_CITIES``.
    """
    return list(config.SUPPORTED_CITIES.keys())


def get_city_center(city_name):
    """
    Return the (lat, lon) center coordinates for *city_name*.

    Args:
        city_name: A key from ``config.SUPPORTED_CITIES``.

    Returns:
        tuple[float, float]: ``(latitude, longitude)`` of the city center,
        or the default city's center if *city_name* is unknown.
    """
    city_info = config.SUPPORTED_CITIES.get(city_name)
    if city_info is not None:
        return city_info["center"]
    # Fall back to default city center
    default_info = config.SUPPORTED_CITIES.get(config.DEFAULT_CITY, {})
    return default_info.get("center", (53.3498, -6.2603))
