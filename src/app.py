"""Main application entry point for the DSAI Webapp."""

import os
import sys

import streamlit as st

# Add src to Python path if running from root
if os.path.exists("src"):
    print("Setting path to /src")
    sys.path.insert(0, "src")

from utils import get_config, get_version

# --- CONFIG ---
st.set_page_config(
    page_title="Datascience & Artifical Intelligence 5BHIF",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Get application version
APP_VERSION = get_version()
ENVIRONMENT = get_config("ENVIRONMENT_NAME", "development")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")

# Determine pages directory
pages_dir = "pages"

# Define pages
homepage = st.Page(f"./{pages_dir}/homepage.py", title="Startseite")
gradient_descent = st.Page(f"./{pages_dir}/gradient-descent.py", title="Gradient Descent")
perceptron = st.Page(f"./{pages_dir}/perceptron.py", title="Perceptron")
knn_visualizer = st.Page(f"./{pages_dir}/knn-visualize.py", title="KNN Visualizer")
neuronal_net = st.Page(f"./{pages_dir}/neuronal-net.py", title="Neuronal Network")

# Navigation (homepage first)
pg = st.navigation([homepage, gradient_descent, perceptron, knn_visualizer, neuronal_net])

# Run the selected page
pg.run()

# --- Footer ---
st.markdown("---")

# Show environment in non-production
footer_text = f"© 2025 Kofler Phillip HTL V - Informatik ({APP_VERSION})"
if ENVIRONMENT != "production":
    footer_text += f" - {ENVIRONMENT.upper()}"

st.markdown(
    f"<div style='text-align:center;'>{footer_text}</div>",
    unsafe_allow_html=True,
)
