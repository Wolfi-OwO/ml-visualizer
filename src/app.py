import os
import sys

import streamlit as st

from utils import get_config, get_version

# Add src to Python path if running from root
if os.path.exists("src"):
    print("Setting path to /src")
    sys.path.insert(0, "src")


# --- CONFIG ---
st.set_page_config(
    page_title="ML Visualizer - Interactive Machine Learning Diagrams",
    layout="wide",
)

# Load CSS - handle both local and docker paths
css_base = "./src/styles" if os.path.exists("./src/styles") else "./styles"
st.markdown("<style>" + open(f"{css_base}/sidebar.css").read() + "</style>", unsafe_allow_html=True)
st.markdown("<style>" + open(f"{css_base}/index.css").read() + "</style>", unsafe_allow_html=True)


# Get application version
APP_VERSION = get_version()
ENVIRONMENT = get_config("ENVIRONMENT_NAME", "development")

# Determine pages directory
pages_dir = "pages"

# Define pages
pages = [
    st.Page(f"./{pages_dir}/homepage.py", title="Startseite"),
    st.Page(f"./{pages_dir}/gradient-descent.py", title="Gradient Descent"),
    st.Page(f"./{pages_dir}/perceptron.py", title="Perceptron"),
    st.Page(f"./{pages_dir}/knn-visualize.py", title="KNN Visualizer"),
    st.Page(f"./{pages_dir}/neuronal-net.py", title="Neuronal Network"),
]


# Navigation (homepage first)
pg = st.navigation(pages)
pg.run()


# --- Footer ---
st.markdown("---")

# Footer
footer_text = f'<span> Copyright © 2025 <a href="mailto:koflerphillip@gmail.com">Kofler Phillip</a>, HTL Villach - Informatik ({APP_VERSION})'
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
