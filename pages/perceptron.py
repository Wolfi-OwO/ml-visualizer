import time

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

st.title("Perceptron Visualisierung")

st.markdown(
    """
    Hier siehst du ein einfaches neuronales Netzwerk (Perceptron), das lernt,
    den AND-Operator zu erkennen.
    Die Gewichte ändern sich bei jedem Trainingsschritt - sichtbar im Netzwerkdiagramm.
    """
)  # Trainingsdaten
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([0, 0, 0, 1])

# Sidebar-Parameter
st.sidebar.subheader("Einstellungen - Perceptron")
lr = st.sidebar.slider("Lernrate η", 0.01, 1.0, 0.3, 0.01)
epochs = st.sidebar.slider("Epochen", 1, 20, 5)
animate = st.sidebar.button("Training starten")

# Initialisierung
np.random.seed(42)
w = np.random.uniform(-1, 1, 2)
b = np.random.uniform(-1, 1)
history = [(w.copy(), b)]

for _epoch in range(epochs):
    for i in range(len(X)):
        z = np.dot(X[i], w) + b
        y_hat = 1 if z > 0 else 0
        error = y[i] - y_hat
        w += lr * error * X[i]
        b += lr * error
        history.append((w.copy(), b))

placeholder = st.empty()


def draw_network(weights, bias, step):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axis("off")

    input_pos = [(0, 1), (0, -1)]
    neuron_pos = (2, 0)
    output_pos = (4, 0)

    # Inputs
    for i, pos in enumerate(input_pos):
        ax.scatter(*pos, s=1000, color="skyblue")
        ax.text(pos[0], pos[1], f"x{i+1}", ha="center", va="center", fontsize=12)

    # Neuron
    ax.scatter(*neuron_pos, s=1200, color="lightgreen")
    ax.text(neuron_pos[0], neuron_pos[1], "Neuron", ha="center", va="center", fontsize=11)

    # Output
    ax.scatter(*output_pos, s=1000, color="orange")
    ax.text(output_pos[0], output_pos[1], "y", ha="center", va="center", fontsize=12)

    # Connections
    for i, pos in enumerate(input_pos):
        color = "red" if weights[i] < 0 else "green"
        ax.plot(
            [pos[0], neuron_pos[0]],
            [pos[1], neuron_pos[1]],
            color=color,
            lw=3,
            alpha=0.8,
        )
        mid_x = (pos[0] + neuron_pos[0]) / 2
        mid_y = (pos[1] + neuron_pos[1]) / 2
        ax.text(mid_x, mid_y + 0.3, f"w{i+1}={weights[i]:.2f}", fontsize=10, color=color)

    # Bias connection
    ax.text(3, 0.4, f"Bias={bias:.2f}", color="purple", fontsize=10)

    ax.set_title(f"Perceptron Netzwerk - Schritt {step}")
    return fig


if animate:
    for step in range(len(history)):
        w, b = history[step]
        fig = draw_network(w, b, step)
        placeholder.pyplot(fig)
        time.sleep(0.4)
else:
    step = st.slider("Manueller Schritt", 0, len(history) - 1, 0)
    w, b = history[step]
    fig = draw_network(w, b, step)
    st.pyplot(fig)

st.info(f"Aktueller Zustand → w₁={w[0]:.2f}, w₂={w[1]:.2f}, Bias={b:.2f}")

# Code Expander
with st.expander("Code für Perceptron kopieren"):
    perceptron_code = """
import numpy as np

X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([0, 0, 0, 1])

lr = 0.3
epochs = 5

np.random.seed(42)
w = np.random.uniform(-1, 1, 2)
b = np.random.uniform(-1, 1)

for epoch in range(epochs):
    for i in range(len(X)):
        z = np.dot(X[i], w) + b
        y_hat = 1 if z > 0 else 0
        error = y[i] - y_hat
        w += lr * error * X[i]
        b += lr * error

print("Finale Gewichte:", w, "Bias:", b)
"""
    st.code(perceptron_code, language="python")
