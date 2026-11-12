"""
Statistics and Detailed Route Inspection Component.
"""

import streamlit as st
import config
from visualization.metrics import (
    format_distance,
    format_time,
    format_execution_time,
    format_nodes,
    get_algorithm_emoji,
)


def render_statistics(results_dict):
    """
    Render individual metric cards and node-by-node route details for each algorithm.

    Args:
        results_dict: dict of algorithm_name -> AlgorithmResult.
    """
    st.markdown("### 📋 Route Diagnostics & Inspection")

    if not results_dict:
        st.info("No route evaluations available. Click 'Dispatch & Calculate Routes' in the sidebar.")
        return

    # Algorithm metric cards
    cols = st.columns(len(results_dict))
    for i, (name, res) in enumerate(results_dict.items()):
        color = config.ALGORITHM_COLORS.get(name, "#ffffff")
        emoji = get_algorithm_emoji(name)

        with cols[i]:
            st.markdown(
                f"""
                <div class="dashboard-card" style="border-top: 4px solid {color};">
                    <h3 style="margin-top:0; color:{color};">{emoji} {name}</h3>
                    <p style="margin: 0.2rem 0; font-size: 0.85rem;">
                        <strong>Status:</strong> {'✅ Found' if res.found else '❌ Unreachable'}
                    </p>
                    <p style="margin: 0.2rem 0; font-size: 0.85rem;">
                        <strong>Distance:</strong> {format_distance(res.total_distance)}
                    </p>
                    <p style="margin: 0.2rem 0; font-size: 0.85rem;">
                        <strong>Travel Time:</strong> {format_time(res.total_travel_time)}
                    </p>
                    <p style="margin: 0.2rem 0; font-size: 0.85rem;">
                        <strong>Nodes Explored:</strong> {format_nodes(res.nodes_explored)}
                    </p>
                    <p style="margin: 0.2rem 0; font-size: 0.85rem;">
                        <strong>Runtime:</strong> {format_execution_time(res.execution_time)}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Detailed expandable node-by-node sequence
    st.markdown("#### 🔍 Waypoint & Node Sequences")
    for name, res in results_dict.items():
        emoji = get_algorithm_emoji(name)
        with st.expander(f"{emoji} {name} Route Path ({len(res.path)} waypoints)"):
            if res.found and res.path:
                st.write(f"**Node Traversal Sequence ({len(res.path)} nodes):**")
                path_str = " ➔ ".join(str(n) for n in res.path[:50])
                if len(res.path) > 50:
                    path_str += f" ... (+{len(res.path) - 50} more nodes) ➔ {res.path[-1]}"
                st.code(path_str, language="text")
                st.caption(f"Traversed {res.edges_traversed} edges across {res.nodes_explored} explored network vertices.")
            else:
                st.warning(f"No traversable route found between source and destination using {name}.")

