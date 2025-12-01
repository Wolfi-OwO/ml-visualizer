import os

import streamlit as st

# --- CONFIG ---
st.set_page_config(page_title="ML Visualizer", layout="centered")


# Read version dynamically from VERSION file
def get_version():
    try:
        # First try current directory (Docker environment)
        if os.path.exists("VERSION"):
            with open("VERSION") as f:
                return f.read().strip()
        # Then try parent directory (local development)
        elif os.path.exists("../VERSION"):
            with open("../VERSION") as f:
                return f.read().strip()
        else:
            return "1.0.0"  # Default fallback
    except Exception:
        return "1.0.0"  # Error fallback


APP_VERSION = get_version()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Options")

gradient_descent = st.Page("./pages/gradient-descent.py", title="Gradient Descent")
perceptron = st.Page("./pages/perceptron.py", title="Perceptron")
knn_visualizer = st.Page("./pages/knn-visualize.py", title="KNN Visualizer")
neuronal_net = st.Page("./pages/neuronal-net.py", title="Neuronal Network")

pg = st.navigation([gradient_descent, perceptron, knn_visualizer, neuronal_net])
st.set_page_config(page_title="ML Visualizer", page_icon=":material/edit:")
pg.run()

# --- Footer ---
st.markdown("---")
st.markdown(
    f"<div style='text-align:center;'>© 2025 Kofler Phillip HTL V - Informatik (V. {APP_VERSION})</div>",
    unsafe_allow_html=True,
)
