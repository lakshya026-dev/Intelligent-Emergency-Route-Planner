"""
Format algorithm metrics for dashboard display.

Provides human-readable formatting for distances, times, node counts, and
per-algorithm emoji labels.  Also builds metric-card dictionaries suitable
for Streamlit / front-end rendering.
"""

from __future__ import annotations

from algorithms.algorithm_utils import AlgorithmResult


# ──────────────────────────────────────────────
# Formatting helpers
# ──────────────────────────────────────────────

def format_distance(meters: float) -> str:
    """Format a distance in meters to a human-readable string.

    Examples:
        >>> format_distance(2350)
        '2.35 km'
        >>> format_distance(450)
        '450 m'
    """
    if meters >= 1000:
        return f"{meters / 1000:.2f} km"
    return f"{meters:.0f} m"


def format_time(seconds: float) -> str:
    """Format a duration in seconds to a human-readable string.

    Examples:
        >>> format_time(330)
        '5 min 30 sec'
        >>> format_time(8100)
        '2 hr 15 min'
    """
    if seconds < 60:
        return f"{seconds:.0f} sec"

    hours = int(seconds // 3600)
    remaining = seconds - hours * 3600
    minutes = int(remaining // 60)
    secs = int(remaining % 60)

    if hours > 0:
        parts = [f"{hours} hr"]
        if minutes:
            parts.append(f"{minutes} min")
        return " ".join(parts)

    parts = [f"{minutes} min"]
    if secs:
        parts.append(f"{secs} sec")
    return " ".join(parts)


def format_execution_time(seconds: float) -> str:
    """Format an execution time in seconds to ms or s.

    Examples:
        >>> format_execution_time(0.0125)
        '12.5 ms'
        >>> format_execution_time(1.234)
        '1.23 s'
    """
    if seconds < 1:
        return f"{seconds * 1000:.1f} ms"
    return f"{seconds:.2f} s"


def format_nodes(count: int) -> str:
    """Format a node count with comma separators.

    Examples:
        >>> format_nodes(1234)
        '1,234'
    """
    return f"{count:,}"


# ──────────────────────────────────────────────
# Emoji mapping
# ──────────────────────────────────────────────

_ALGORITHM_EMOJIS: dict[str, str] = {
    "BFS": "🔵",
    "DFS": "🟠",
    "Greedy": "🟣",
    "A*": "🟢",
}


def get_algorithm_emoji(name: str) -> str:
    """Return the emoji associated with an algorithm name.

    Args:
        name: Algorithm name (e.g. 'BFS', 'A*').

    Returns:
        The emoji string, or '⚪' if the name is unrecognised.
    """
    return _ALGORITHM_EMOJIS.get(name, "⚪")


# ──────────────────────────────────────────────
# Metric card builder
# ──────────────────────────────────────────────

def create_metric_card_data(result: AlgorithmResult) -> dict:
    """Build a dict of formatted metric fields for display.

    Args:
        result: An AlgorithmResult instance from a completed algorithm run.

    Returns:
        A dictionary with keys:
            algorithm_name, emoji, found, distance, travel_time,
            execution_time, nodes_explored, edges_traversed, path_length.
    """
    return {
        "algorithm_name": result.algorithm_name,
        "emoji": get_algorithm_emoji(result.algorithm_name),
        "found": result.found,
        "distance": format_distance(result.total_distance) if result.found else "N/A",
        "travel_time": format_time(result.total_travel_time) if result.found else "N/A",
        "execution_time": format_execution_time(result.execution_time),
        "nodes_explored": format_nodes(result.nodes_explored),
        "edges_traversed": format_nodes(result.edges_traversed),
        "path_length": format_nodes(len(result.path)) if result.path else "0",
    }
