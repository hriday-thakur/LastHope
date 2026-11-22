"""
Theme manager for LastHope.
Injects custom modern brutalist / Swiss editorial CSS.
"""

from pathlib import Path
import streamlit as st

_CSS_PATH = Path(__file__).parent / "styles.css"


def inject_css() -> None:
    """Reads styles.css and injects it once into the Streamlit app."""
    if _CSS_PATH.exists():
        css = _CSS_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>\n{css}\n</style>", unsafe_allow_html=True)
