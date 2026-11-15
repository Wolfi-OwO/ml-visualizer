import time

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.theme import (
    CANVAS,
    CONTRAST,
    HIGHLIGHT,
    INK,
    MUTED,
    NEGATIVE,
    PANEL,
    POSITIVE,
    RULE,
    SIGNAL,
)

DEFAULT_CONFIG = {
    "lr": 0.3,
    "epochs": 6,
    "seed": 42,
    "animate": True,
}

st.title("Perceptron")
st.caption(
    "Ein einzelnes Neuron: zwei Eingänge, ein Ausgang – trainiert auf die AND-Wahrheitstabelle."
)

X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
y = np.array([0, 0, 0, 1], dtype=int)


def predict_labels(weights: np.ndarray, bias: float) -> np.ndarray:
    return (np.dot(X, weights) + bias >= 0).astype(int)


@st.cache_data(show_spinner=False)
def build_history(
    learning_rate: float, epoch_count: int, random_seed: int
) -> list[dict[str, object]]:
    rng = np.random.default_rng(random_seed)
    weights = rng.uniform(-1.0, 1.0, size=2)
    bias = float(rng.uniform(-1.0, 1.0))
    history: list[dict[str, object]] = []

    def snapshot(step: int, epoch: int, sample_index: int) -> None:
        predictions = predict_labels(weights, bias)
        history.append(
            {
                "step": step,
                "epoch": epoch,
                "sample_index": sample_index,
                "weights": weights.copy(),
                "bias": float(bias),
                "predictions": predictions,
                "accuracy": float(np.mean(predictions == y)),
            }
        )

    snapshot(step=0, epoch=0, sample_index=-1)
    step = 1

    for epoch in range(1, epoch_count + 1):
        for sample_index, features in enumerate(X):
            raw = float(np.dot(features, weights) + bias)
            prediction = 1 if raw >= 0 else 0
            error = y[sample_index] - prediction
            weights = weights + learning_rate * error * features
            bias = float(bias + learning_rate * error)
            snapshot(step=step, epoch=epoch, sample_index=sample_index)
            step += 1

    return history


def edge_color(weight: float, highlighted: bool) -> str:
    if highlighted:
        return HIGHLIGHT
    return POSITIVE if weight >= 0 else NEGATIVE


def node_color(value: float, highlighted: bool) -> str:
    if highlighted:
        return HIGHLIGHT
    if value >= 0.5:
        return SIGNAL
    return MUTED


def build_perceptron_figure(
    weights: np.ndarray,
    bias: float,
    inputs: np.ndarray,
    sim_step: int,
) -> go.Figure:
    x_positions = [0.0, 0.0, 1.8]
    y_positions = [0.75, 0.25, 0.5]

    z = float(np.dot(inputs, weights) + bias)
    output = float(1.0 if z >= 0 else 0.0)

    fig = go.Figure()

    for i, start_y in enumerate(y_positions[:2]):
        highlighted = sim_step == 1
        weight = float(weights[i])
        fig.add_trace(
            go.Scatter(
                x=[x_positions[i], x_positions[2]],
                y=[start_y, y_positions[2]],
                mode="lines",
                line={
                    "color": edge_color(weight, highlighted),
                    "width": max(2.0, 2.5 + abs(weight) * 1.8),
                },
                hoverinfo="text",
                text=f"w{i + 1} = {weight:+.3f}",
                showlegend=False,
            )
        )

    node_text = [
        f"x₁ = {int(inputs[0])}",
        f"x₂ = {int(inputs[1])}",
        f"ŷ = {int(output)}",
    ]
    node_values = [float(inputs[0]), float(inputs[1]), output]
    node_highlights = [sim_step == 0, sim_step == 0, sim_step >= 2]
    node_colors = [
        node_color(value, highlighted)
        for value, highlighted in zip(node_values, node_highlights, strict=False)
    ]

    fig.add_trace(
        go.Scatter(
            x=x_positions,
            y=y_positions,
            mode="markers+text",
            marker={"size": 60, "color": node_colors, "line": {"width": 2, "color": CANVAS}},
            text=node_text,
            textposition="middle center",
            # Override the figure-wide INK font: node fill is HIGHLIGHT/SIGNAL/
            # MUTED (from node_color()), and INK-on-those measured 1.25-2.57:1 --
            # under the 3:1 WCAG floor. CANVAS clears 6.2:1+ on all of them.
            textfont={"color": CANVAS, "size": 12},
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.add_annotation(
        x=1.8,
        y=0.18,
        text=f"z = w·x + b = {z:+.3f}<br>b = {bias:+.3f}",
        showarrow=False,
        font={"size": 12, "color": INK},
        align="left",
        bgcolor=PANEL,
        bordercolor=RULE,
        borderwidth=1,
    )

    fig.update_layout(
        height=360,
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": INK},
        xaxis={"visible": False, "range": [-0.4, 2.3]},
        yaxis={"visible": False, "range": [0.0, 1.0]},
    )
    return fig


def build_training_figure(history: list[dict[str, object]]) -> go.Figure:
    df = pd.DataFrame(
        {
            "step": [row["step"] for row in history],
            "accuracy": [row["accuracy"] for row in history],
        }
    )
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["step"],
            y=df["accuracy"],
            mode="lines",
            name="Accuracy",
            line={"color": CONTRAST, "width": 3},
        )
    )
    fig.update_layout(
        height=260,
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": INK},
        yaxis={"title": "Accuracy", "range": [0, 1], "gridcolor": RULE},
        xaxis={"title": "Step", "gridcolor": RULE},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0.0},
    )
    return fig


if "perceptron_config" not in st.session_state:
    st.session_state.perceptron_config = DEFAULT_CONFIG.copy()
if "perceptron_current_step" not in st.session_state:
    st.session_state.perceptron_current_step = 0
if "perceptron_is_animating" not in st.session_state:
    st.session_state.perceptron_is_animating = False
if "perceptron_start_requested" not in st.session_state:
    st.session_state.perceptron_start_requested = False
if "perceptron_step_widget" not in st.session_state:
    st.session_state.perceptron_step_widget = 0

st.sidebar.header("Inputs")
input1 = st.sidebar.slider("Input 1", 0, 1, 0, step=1)
input2 = st.sidebar.slider("Input 2", 0, 1, 0, step=1)

st.sidebar.subheader("Training")
with st.sidebar.form("perceptron_controls"):
    lr_input = st.slider(
        "Lernrate η", 0.01, 1.0, float(st.session_state.perceptron_config["lr"]), 0.01
    )
    epochs_input = st.slider("Epochen", 1, 20, int(st.session_state.perceptron_config["epochs"]))
    seed_input = st.number_input(
        "Seed",
        min_value=0,
        max_value=9999,
        value=int(st.session_state.perceptron_config["seed"]),
        step=1,
    )
    animate_input = st.checkbox(
        "Training animieren",
        value=bool(st.session_state.perceptron_config["animate"]),
    )
    start = st.form_submit_button("Training starten", type="primary")

stop_animation = st.sidebar.button("Animation stoppen")

if start:
    st.session_state.perceptron_config = {
        "lr": float(lr_input),
        "epochs": int(epochs_input),
        "seed": int(seed_input),
        "animate": bool(animate_input),
    }
    st.session_state.perceptron_start_requested = True

config = st.session_state.perceptron_config
history = build_history(config["lr"], config["epochs"], config["seed"])
max_step = len(history) - 1

if st.session_state.perceptron_start_requested:
    if config["animate"]:
        st.session_state.perceptron_current_step = 0
        st.session_state.perceptron_is_animating = True
    else:
        st.session_state.perceptron_current_step = max_step
        st.session_state.perceptron_is_animating = False
    st.session_state.perceptron_step_widget = st.session_state.perceptron_current_step
    st.session_state.perceptron_start_requested = False

if stop_animation:
    st.session_state.perceptron_is_animating = False

st.session_state.perceptron_current_step = min(
    int(st.session_state.perceptron_current_step), max_step
)
if st.session_state.perceptron_is_animating:
    st.session_state.perceptron_step_widget = st.session_state.perceptron_current_step
step_value = st.sidebar.slider(
    "Trainingsschritt",
    0,
    max_step,
    key="perceptron_step_widget",
)
st.session_state.perceptron_current_step = int(step_value)

snapshot = history[st.session_state.perceptron_current_step]
weights = np.asarray(snapshot["weights"], dtype=float)
bias = float(snapshot["bias"])

inputs = np.array([input1, input2], dtype=float)
z = float(np.dot(inputs, weights) + bias)
predicted_output = int(z >= 0)
expected_output = int(input1 & input2)

step_texts = {
    0: "Inputs setzen",
    1: "Gewichte anwenden: z = w·x + b",
    2: "Schwellwert: ŷ = 1 falls z ≥ 0",
}
sim_step = st.sidebar.slider("Signalfluss", 0, 2, 0)

visual_col, side_col = st.columns([2, 1], gap="large")

with visual_col:
    st.subheader("Das Neuron")
    st.plotly_chart(build_perceptron_figure(weights, bias, inputs, sim_step), width="stretch")
    st.info(step_texts[sim_step])
    st.subheader("Trainingsverlauf")
    st.plotly_chart(build_training_figure(history), width="stretch")

with side_col:
    st.subheader("Aktueller Schritt")
    st.metric("Schritt", int(snapshot["step"]))
    st.metric("Epoche", int(snapshot["epoch"]))
    st.metric("w₁", f"{weights[0]:+.3f}")
    st.metric("w₂", f"{weights[1]:+.3f}")
    st.metric("Bias", f"{bias:+.3f}")
    st.metric("Accuracy", f"{float(snapshot['accuracy']) * 100:.0f}%")
    st.divider()
    st.metric("Erwartet (AND)", expected_output)
    st.metric("Vorhergesagt", predicted_output)
    st.write(f"`z = {z:+.3f}`")

st.divider()
st.subheader("Wahrheitstabelle")
truth_table = pd.DataFrame(
    {
        "Input 1": X[:, 0].astype(int),
        "Input 2": X[:, 1].astype(int),
        "Expected": y,
        "Predicted": np.asarray(snapshot["predictions"], dtype=int),
    }
)
st.table(truth_table)

with st.expander("Erklärung", expanded=False):
    st.markdown(
        r"""
Ein Perceptron ist ein einzelnes Neuron, ohne Hidden Layer, ohne alles. Es gewichtet
seine Eingänge, addiert einen Bias dazu und schaut nur noch nach, ob das Ergebnis
über null liegt:

$$z = w_1 x_1 + w_2 x_2 + b
\qquad
\hat{y} = \begin{cases}1 & \text{wenn } z \ge 0\\0 & \text{sonst}\end{cases}$$

Gelernt wird stur nach Fehler. Das Neuron rät ein Beispiel, vergleicht mit der
richtigen Antwort und rechnet die Differenz aus. Stimmt die Vorhersage, bleibt alles,
wie es ist. Liegt sie daneben, wandern die Gewichte um einen Lernraten-Anteil in die
Richtung, die den Fehler kleiner gemacht hätte:

$$w \leftarrow w + \eta \cdot (y - \hat{y}) \cdot x
\qquad
b \leftarrow b + \eta \cdot (y - \hat{y})$$

Geometrisch ist $z = 0$ eine Gerade, und jedes Update kippt oder verschiebt sie.
Bei AND lässt sich eine Gerade finden, die die einzige Eins von den drei Nullen
trennt, deshalb funktioniert das hier. Bei XOR gäbe es keine solche Gerade, und
das Perceptron würde ewig weiterruckeln, ohne je fertig zu werden.
        """
    )

if st.session_state.perceptron_is_animating:
    if st.session_state.perceptron_current_step < max_step:
        time.sleep(0.18)
        st.session_state.perceptron_current_step += 1
        st.rerun()
    else:
        st.session_state.perceptron_is_animating = False
