"""
Dashboard Header and Incident Status Card Components.
"""

import streamlit as st
import config


def render_dashboard_header(city: str, vehicle_type: str, start_node, goal_node, traffic_condition: str):
    """
    Render the top operations center header and summary cards.
    """
    traffic_color = config.TRAFFIC_CONDITIONS.get(traffic_condition, {}).get("color", "#34d399")
    st.markdown(
        f"""
        <div class="emergency-header">
            <div class="header-main">
                <div class="brand-mark">✦</div>
                <div><div class="eyebrow">CSE276 · AI FOUNDATIONS · OPERATIONS SUITE</div>
                    <h1>{config.DASHBOARD_TITLE}</h1>
                    <p>Emergency dispatch · Intelligent road network analysis</p></div>
            </div>
            <div class="header-status">
                <span class="header-chip">⌖ {city}</span>
                <span class="header-chip operational"><i></i> SYSTEM OPERATIONAL</span>
                <span class="header-chip simulation" style="--traffic-color:{traffic_color}"><i></i> LIVE SIMULATION · {traffic_condition.upper()}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 Status Cards Row
    col1, col2, col3, col4 = st.columns(4)

    veh_cfg = config.EMERGENCY_VEHICLES.get(vehicle_type, {})
    traffic_cfg = config.TRAFFIC_CONDITIONS.get(traffic_condition, {})

    with col1:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">DISPATCHED UNIT</div>
                <div class="metric-value">{veh_cfg.get('icon', '🚑')} {vehicle_type}</div>
                <div class="metric-delta" style="color: #22c55e;">Priority Level {veh_cfg.get('priority', 1)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">ORIGIN · DISPATCH</div>
                <div class="metric-value" style="font-size: 1.15rem;">Node {start_node if start_node is not None else 'N/A'}</div>
                <div class="metric-delta" style="color: #3b82f6;">Active Ready</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">DESTINATION · INCIDENT</div>
                <div class="metric-value" style="font-size: 1.15rem;">Node {goal_node if goal_node is not None else 'N/A'}</div>
                <div class="metric-delta" style="color: #ef4444;">Target Site</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">NETWORK CONDITIONS</div>
                <div class="metric-value" style="color: {traffic_cfg.get('color', '#2ecc71')}; font-size: 1.25rem;">
                    {traffic_condition}
                </div>
                <div class="metric-delta" style="color: {traffic_cfg.get('color', '#2ecc71')};">
                    {traffic_cfg.get('multiplier', 1.0)}x Congestion Factor
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

