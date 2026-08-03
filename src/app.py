from datetime import datetime
from pathlib import Path

import streamlit as st

from utils import get_config, get_version

SRC_DIR = Path(__file__).resolve().parent


def load_stylesheet(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# --- CONFIG ---
st.set_page_config(
    page_title="ML Visualizer - Interactive Machine Learning Diagrams",
    page_icon=str(SRC_DIR / "assets" / "favicon.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

styles_dir = SRC_DIR / "styles"
for stylesheet in ("sidebar.css", "index.css"):
    st.markdown(
        f"<style>{load_stylesheet(styles_dir / stylesheet)}</style>",
        unsafe_allow_html=True,
    )


# Get application version
APP_VERSION = get_version()
ENVIRONMENT = get_config("ENVIRONMENT_NAME", "development")

pages_dir = SRC_DIR / "pages"

# Define pages
pages = [
    st.Page(str(pages_dir / "homepage.py"), title="Startseite"),
    st.Page(str(pages_dir / "gradient-descent.py"), title="Gradient Descent"),
    st.Page(str(pages_dir / "perceptron.py"), title="Perceptron"),
    st.Page(str(pages_dir / "knn-visualize.py"), title="KNN Visualizer"),
    st.Page(str(pages_dir / "neuronal-net.py"), title="Neural Network"),
]


# Navigation (homepage first)
pg = st.navigation(pages)
pg.run()


# --- Footer ---
st.markdown("---")

# Footer
footer_text = (
    f"<span>Copyright © {datetime.now().year} "
    f'<a href="mailto:koflerphillip@gmail.com">Kofler Phillip</a>, '
    f"HTL Villach - Informatik ({APP_VERSION})"
)
if ENVIRONMENT != "production":
    footer_text += f" - {ENVIRONMENT.upper()}"
footer_text += "</span>"

st.markdown(
    f"""
    <div class="footer">
        {footer_text}
    </div>
    """,
    unsafe_allow_html=True,
)
