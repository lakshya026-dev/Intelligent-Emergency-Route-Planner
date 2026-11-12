"""
Map Component for displaying the interactive Folium map in Streamlit.
"""

import streamlit as st

try:
    from streamlit_folium import st_folium
    HAS_STREAMLIT_FOLIUM = True
except ImportError:
    HAS_STREAMLIT_FOLIUM = False


def render_map(folium_map, height: int = 560):
    """
    Render a Folium map using streamlit_folium or fallback to HTML display.

    Args:
        folium_map: folium.Map instance.
        height: Display height in pixels.
    """
    if folium_map is None:
        st.warning("No map generated to display.")
        return None

    if HAS_STREAMLIT_FOLIUM:
        try:
            return st_folium(
                folium_map,
                width="100%",
                height=height,
                returned_objects=["last_clicked"],
            )
        except Exception:
            # Graceful fallback to native Streamlit HTML rendering (e.g. if pyarrow is missing)
            map_html = folium_map._repr_html_()
            st.components.v1.html(map_html, height=height)
            return None
    else:
        # Fallback to direct HTML rendering if streamlit_folium is missing
        map_html = folium_map._repr_html_()
        st.components.v1.html(map_html, height=height)
        return None

