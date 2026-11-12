"""
Plotly charts for algorithm comparison and traffic analysis.

All charts use the ``plotly_dark`` template for a cohesive dark-themed
dashboard and pull colors from ``config.ALGORITHM_COLORS`` /
``config.TRAFFIC_CONDITIONS``.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import config


# ──────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────
def _extract_successful(results_dict: dict) -> dict:
    """Return only those results where the algorithm found a path."""
    return {name: r for name, r in results_dict.items() if r.found}


def _algo_color(name: str) -> str:
    """Return the configured color for an algorithm, or a fallback grey."""
    return config.ALGORITHM_COLORS.get(name, "#95a5a6")


# ──────────────────────────────────────────────
# Individual metric charts
# ──────────────────────────────────────────────

def create_execution_time_chart(results_dict: dict) -> go.Figure:
    """Bar chart comparing algorithm execution times (ms).

    Args:
        results_dict: Dict mapping algorithm_name -> AlgorithmResult.

    Returns:
        A Plotly Figure.
    """
    successful = _extract_successful(results_dict)
    names = list(successful.keys())
    times = [r.execution_time * 1000 for r in successful.values()]  # seconds → ms
    colors = [_algo_color(n) for n in names]

    fig = go.Figure(
        data=[go.Bar(x=names, y=times, marker_color=colors, text=[f"{t:.2f}" for t in times], textposition="auto")],
    )
    fig.update_layout(
        title="Execution Time Comparison",
        xaxis_title="Algorithm",
        yaxis_title="Time (ms)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#cbd5e1"),
        margin=dict(l=18, r=18, t=58, b=24),
    )
    return fig


def create_nodes_explored_chart(results_dict: dict) -> go.Figure:
    """Bar chart of nodes explored per algorithm.

    Args:
        results_dict: Dict mapping algorithm_name -> AlgorithmResult.

    Returns:
        A Plotly Figure.
    """
    successful = _extract_successful(results_dict)
    names = list(successful.keys())
    nodes = [r.nodes_explored for r in successful.values()]
    colors = [_algo_color(n) for n in names]

    fig = go.Figure(
        data=[go.Bar(x=names, y=nodes, marker_color=colors, text=[f"{n:,}" for n in nodes], textposition="auto")],
    )
    fig.update_layout(
        title="Nodes Explored Comparison",
        xaxis_title="Algorithm",
        yaxis_title="Nodes Explored",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#cbd5e1"),
        margin=dict(l=18, r=18, t=58, b=24),
    )
    return fig


def create_distance_comparison_chart(results_dict: dict) -> go.Figure:
    """Bar chart of path distances (km).

    Args:
        results_dict: Dict mapping algorithm_name -> AlgorithmResult.

    Returns:
        A Plotly Figure.
    """
    successful = _extract_successful(results_dict)
    names = list(successful.keys())
    distances = [r.total_distance / 1000 for r in successful.values()]  # m → km
    colors = [_algo_color(n) for n in names]

    fig = go.Figure(
        data=[go.Bar(x=names, y=distances, marker_color=colors, text=[f"{d:.2f}" for d in distances], textposition="auto")],
    )
    fig.update_layout(
        title="Path Distance Comparison",
        xaxis_title="Algorithm",
        yaxis_title="Distance (km)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#cbd5e1"), margin=dict(l=18, r=18, t=58, b=24),
    )
    return fig


def create_travel_time_chart(results_dict: dict) -> go.Figure:
    """Bar chart of estimated travel times (minutes).

    Args:
        results_dict: Dict mapping algorithm_name -> AlgorithmResult.

    Returns:
        A Plotly Figure.
    """
    successful = _extract_successful(results_dict)
    names = list(successful.keys())
    times = [r.total_travel_time / 60 for r in successful.values()]  # s → min
    colors = [_algo_color(n) for n in names]

    fig = go.Figure(
        data=[go.Bar(x=names, y=times, marker_color=colors, text=[f"{t:.1f}" for t in times], textposition="auto")],
    )
    fig.update_layout(
        title="Travel Time Comparison",
        xaxis_title="Algorithm",
        yaxis_title="Travel Time (min)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#cbd5e1"), margin=dict(l=18, r=18, t=58, b=24),
    )
    return fig


# ──────────────────────────────────────────────
# Comprehensive subplot comparison
# ──────────────────────────────────────────────

def create_comprehensive_comparison(results_dict: dict) -> go.Figure:
    """Subplot figure with all four metrics side by side.

    Panels: Execution Time | Nodes Explored | Distance | Travel Time.

    Args:
        results_dict: Dict mapping algorithm_name -> AlgorithmResult.

    Returns:
        A Plotly Figure with four subplots.
    """
    successful = _extract_successful(results_dict)
    names = list(successful.keys())
    colors = [_algo_color(n) for n in names]

    exec_times = [r.execution_time * 1000 for r in successful.values()]
    nodes = [r.nodes_explored for r in successful.values()]
    distances = [r.total_distance / 1000 for r in successful.values()]
    travel_times = [r.total_travel_time / 60 for r in successful.values()]

    fig = make_subplots(
        rows=1,
        cols=4,
        subplot_titles=["Execution Time (ms)", "Nodes Explored", "Distance (km)", "Travel Time (min)"],
        horizontal_spacing=0.08,
    )

    fig.add_trace(go.Bar(x=names, y=exec_times, marker_color=colors, name="Exec Time", showlegend=False), row=1, col=1)
    fig.add_trace(go.Bar(x=names, y=nodes, marker_color=colors, name="Nodes", showlegend=False), row=1, col=2)
    fig.add_trace(go.Bar(x=names, y=distances, marker_color=colors, name="Distance", showlegend=False), row=1, col=3)
    fig.add_trace(go.Bar(x=names, y=travel_times, marker_color=colors, name="Travel Time", showlegend=False), row=1, col=4)

    fig.update_layout(
        title="Comprehensive Algorithm Comparison",
        template="plotly_dark",
        height=400,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#cbd5e1"), margin=dict(l=18, r=18, t=58, b=24),
    )
    return fig


# ──────────────────────────────────────────────
# Traffic distribution
# ──────────────────────────────────────────────

def create_traffic_distribution_chart(traffic_dist: dict) -> go.Figure:
    """Pie chart showing traffic condition distribution.

    Args:
        traffic_dist: Dict mapping condition_name -> count / proportion,
                      e.g. {"Normal": 120, "Moderate": 45, "Heavy": 20, "Severe": 5}.

    Returns:
        A Plotly Figure.
    """
    labels = list(traffic_dist.keys())
    values = list(traffic_dist.values())
    colors = [config.TRAFFIC_CONDITIONS.get(label, {}).get("color", "#95a5a6") for label in labels]

    fig = go.Figure(
        data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors), hole=0.35)],
    )
    fig.update_layout(
        title="Traffic Condition Distribution",
        template="plotly_dark",
    )
    return fig
