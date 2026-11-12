"""
Algorithm Comparison Component for displaying benchmark tables and charts.
"""

import streamlit as st
from visualization.charts import (
    create_comprehensive_comparison,
    create_execution_time_chart,
    create_nodes_explored_chart,
    create_distance_comparison_chart,
    create_travel_time_chart,
)


def render_comparison(results_dict, comparison_df, best_algo_name=None):
    """
    Render comparative benchmark analytics, tables, and Plotly visualizations.

    Args:
        results_dict: dict mapping algorithm_name to AlgorithmResult.
        comparison_df: pandas DataFrame created by ComparisonService.
        best_algo_name: Name of algorithm performing best in primary metric.
    """
    st.markdown("### Algorithm performance comparison")

    if best_algo_name:
        st.markdown(f'<div class="recommendation-banner"><span>RECOMMENDED ROUTE</span><strong>{best_algo_name}</strong><small>Best result for the active routing objective and road conditions.</small></div>', unsafe_allow_html=True)

    # 1. Comparison Metrics Table
    if comparison_df is not None and not comparison_df.empty:
        # st.dataframe imports PyArrow inside Streamlit. Some environments
        # have a PyArrow wheel built for NumPy 2 alongside the project's
        # pinned NumPy 1.x. Render the same live result rows with native
        # Streamlit metrics instead, avoiding that incompatible import path.
        try:
            rows = comparison_df.to_dict(orient="records")
        except (AttributeError, TypeError):
            rows = list(comparison_df)
        if rows:
            columns = list(rows[0].keys())
            table_header = "".join(f"<th>{column}</th>" for column in columns)
            table_rows = "".join(
                "<tr>" + "".join(f"<td>{row.get(column, '—')}</td>" for column in columns) + "</tr>"
                for row in rows
            )
            st.markdown(
                f'<div class="comparison-table-wrap"><table class="comparison-table"><thead><tr>{table_header}</tr></thead><tbody>{table_rows}</tbody></table></div>',
                unsafe_allow_html=True,
            )

    # 2. Interactive Charts
    st.markdown("#### Comparative telemetry")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "All Metrics",
        "Execution Time (ms)",
        "Nodes Explored",
        "Route Distance (m)",
        "Travel Time (s)",
    ])

    with tab1:
        fig_all = create_comprehensive_comparison(results_dict)
        if fig_all:
            st.plotly_chart(fig_all, use_container_width=True)

    with tab2:
        fig_time = create_execution_time_chart(results_dict)
        if fig_time:
            st.plotly_chart(fig_time, use_container_width=True)

    with tab3:
        fig_nodes = create_nodes_explored_chart(results_dict)
        if fig_nodes:
            st.plotly_chart(fig_nodes, use_container_width=True)

    with tab4:
        fig_dist = create_distance_comparison_chart(results_dict)
        if fig_dist:
            st.plotly_chart(fig_dist, use_container_width=True)

    with tab5:
        fig_travel = create_travel_time_chart(results_dict)
        if fig_travel:
            st.plotly_chart(fig_travel, use_container_width=True)

