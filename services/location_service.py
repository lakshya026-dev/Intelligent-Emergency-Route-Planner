"""
Location services.

Provides utilities for selecting, randomising, and validating
graph nodes for route planning.
"""

import random


def get_graph_nodes_as_options(graph, max_nodes=200):
    """
    Return a list of ``(node_id, label)`` tuples for UI dropdown selection.

    Each label shows the node's latitude and longitude rounded to four
    decimal places.

    Args:
        graph: A NetworkX graph with 'y' (lat) and 'x' (lon) node attributes.
        max_nodes: Maximum number of nodes to return (first *max_nodes*
                   from the graph's node iterator).

    Returns:
        list[tuple]: ``[(node_id, "Node <id> (lat, lon)"), ...]``
    """
    options = []
    for idx, (node, data) in enumerate(graph.nodes(data=True)):
        if idx >= max_nodes:
            break
        lat = round(data.get("y", 0.0), 4)
        lon = round(data.get("x", 0.0), 4)
        label = f"Node {node} ({lat}, {lon})"
        options.append((node, label))
    return options


def get_random_start_end(graph, seed=None):
    """
    Return two distinct random node IDs from the graph.

    Args:
        graph: A NetworkX graph.
        seed: Optional random seed for reproducibility.

    Returns:
        tuple: ``(start_node_id, end_node_id)``

    Raises:
        ValueError: If the graph has fewer than two nodes.
    """
    nodes = list(graph.nodes)
    if len(nodes) < 2:
        raise ValueError("Graph must have at least 2 nodes to pick start and end.")
    rng = random.Random(seed)
    start, end = rng.sample(nodes, 2)
    return start, end


def randomize_route_coordinates(graph, node_ids=None):
    """Update Streamlit's origin/destination widget state before widgets render.

    Intended for a button ``on_click`` callback. The graph is passed using
    Streamlit's callback args, and only valid, distinct node IDs are assigned.
    """
    import streamlit as st

    candidates = list(node_ids) if node_ids is not None else (list(graph.nodes) if graph is not None else [])
    if len(candidates) < 2:
        st.session_state.coordinate_randomize_error = "At least two road-network intersections are required."
        return

    start, goal = random.sample(candidates, 2)
    st.session_state.sb_start_node = start
    st.session_state.sb_goal_node = goal
    st.session_state.start_node = start
    st.session_state.goal_node = goal
    st.session_state.coordinate_randomize_error = None


def validate_nodes(graph, start, goal):
    """
    Check that both *start* and *goal* exist in the graph.

    Args:
        graph: A NetworkX graph.
        start: Source node ID.
        goal: Destination node ID.

    Returns:
        tuple[bool, str]: ``(valid, message)`` where *valid* is True when
        both nodes are present.
    """
    missing = []
    if start not in graph:
        missing.append(f"Start node '{start}' not found in graph.")
    if goal not in graph:
        missing.append(f"Goal node '{goal}' not found in graph.")

    if missing:
        return False, " ".join(missing)
    return True, "Both nodes are valid."
