import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Perceptron Visualizer", layout="wide")

st.title("Perceptron - Interaktive Lernvisualisierung")
st.caption(
    "Trainiere das Perceptron auf der AND-Wahrheitstabelle und verfolge jeden Update-Schritt."
)

X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([0, 0, 0, 1])

st.sidebar.header("Einstellungen")
lr = st.sidebar.slider("Lernrate η", 0.01, 1.0, 0.3, 0.01)
epochs = st.sidebar.slider("Epochen", 1, 20, 5)
seed = st.sidebar.number_input("Seed", min_value=0, max_value=9999, value=42, step=1)
animate = st.sidebar.checkbox("Training animieren", value=True)
start = st.sidebar.button("Training starten", type="primary")
stop_animation = st.sidebar.button("Animation stoppen")


def predict_labels(weights: np.ndarray, bias: float) -> np.ndarray:
    return (np.dot(X, weights) + bias >= 0).astype(int)


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


def build_boundary_chart(snapshot: dict[str, object]) -> alt.LayerChart:
    weights = np.asarray(snapshot["weights"], dtype=float)
    bias = float(snapshot["bias"])

    points_df = pd.DataFrame(X, columns=["x", "y"])
    points_df["class"] = y.astype(str)
    points_df["prediction"] = np.asarray(snapshot["predictions"], dtype=int).astype(str)

    points = (
        alt.Chart(points_df)
        .mark_circle(size=220)
        .encode(
            x=alt.X("x:Q", scale=alt.Scale(domain=[-0.2, 1.2]), title="x₁"),
            y=alt.Y("y:Q", scale=alt.Scale(domain=[-0.2, 1.2]), title="x₂"),
            color=alt.Color("class:N", scale=alt.Scale(range=["#f97316", "#2563eb"])),
            tooltip=["x", "y", "class", "prediction"],
        )
    )

    if abs(weights[1]) > 1e-9:
        x_values = np.linspace(-0.2, 1.2, 100)
        y_values = -(weights[0] * x_values + bias) / weights[1]
        line_df = pd.DataFrame({"x": x_values, "y": y_values})
        boundary = alt.Chart(line_df).mark_line(color="#111827", strokeWidth=3).encode(x="x", y="y")
    elif abs(weights[0]) > 1e-9:
        x_boundary = -bias / weights[0]
        boundary = (
            alt.Chart(pd.DataFrame({"x": [x_boundary]}))
            .mark_rule(color="#111827", strokeWidth=3)
            .encode(x="x:Q")
        )
    else:
        boundary = alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_line()

    return (points + boundary).properties(height=420)


history = build_history(lr, epochs, int(seed))
max_step = len(history) - 1

config = (round(float(lr), 4), int(epochs), int(seed))

if "perceptron_current_step" not in st.session_state:
    st.session_state.perceptron_current_step = 0
if "perceptron_is_animating" not in st.session_state:
    st.session_state.perceptron_is_animating = False
if "perceptron_last_config" not in st.session_state:
    st.session_state.perceptron_last_config = config

if st.session_state.perceptron_last_config != config:
    st.session_state.perceptron_last_config = config
    st.session_state.perceptron_current_step = min(
        st.session_state.perceptron_current_step, max_step
    )
    st.session_state.perceptron_is_animating = False

if start:
    if animate:
        st.session_state.perceptron_current_step = 0
        st.session_state.perceptron_is_animating = True
    else:
        st.session_state.perceptron_current_step = max_step
        st.session_state.perceptron_is_animating = False

if stop_animation:
    st.session_state.perceptron_is_animating = False

st.sidebar.slider("Trainingsschritt", 0, max_step, key="perceptron_current_step")
snapshot = history[st.session_state.perceptron_current_step]

st.altair_chart(build_boundary_chart(snapshot), width="stretch")

if st.session_state.perceptron_is_animating:
    st.info(
        "Animation läuft. Die Visualisierung bleibt sichtbar und springt Schritt für Schritt weiter."
    )

metric_col1, metric_col2, metric_col3 = st.columns(3)
with metric_col1:
    st.metric("Aktueller Schritt", int(snapshot["step"]))
    st.metric("Epoche", int(snapshot["epoch"]))
with metric_col2:
    weights = np.asarray(snapshot["weights"], dtype=float)
    st.metric("w₁", f"{weights[0]:.3f}")
    st.metric("w₂", f"{weights[1]:.3f}")
with metric_col3:
    st.metric("Bias", f"{float(snapshot['bias']):.3f}")
    st.metric("Accuracy", f"{float(snapshot['accuracy']) * 100:.0f}%")

truth_table = pd.DataFrame(
    {
        "Input 1": X[:, 0],
        "Input 2": X[:, 1],
        "Expected": y,
        "Predicted": np.asarray(snapshot["predictions"], dtype=int),
    }
)

st.subheader("Aktuelle Vorhersagen")
st.dataframe(truth_table, width="stretch", hide_index=True)

st.subheader("Anleitung")
st.markdown(
    """
    1. Wähle Lernrate, Epochen und bei Bedarf einen neuen Seed.
    2. Starte das Training oder springe mit dem Slider direkt zu einem bestimmten Update.
    3. Die Linie zeigt die aktuelle Entscheidungsgrenze des Perceptrons.
    4. Unten siehst du jederzeit, welche vier AND-Beispiele schon korrekt klassifiziert werden.
    """
)

with st.expander("Erklärung zum Perceptron"):
    st.markdown(
        r"""
Ein **Perceptron** ist das einfachste neuronale Netzwerk.
Es lernt eine **lineare Entscheidungsgrenze**.

### Mathematisches Modell

Das Perceptron berechnet:

$$z = w_1 x_1 + w_2 x_2 + b$$

und wandelt den Wert per Schwellwertfunktion in eine Klasse um.

### Lernregel

Bei einem Fehler werden Gewichte und Bias angepasst:

$$w = w + \eta \cdot error \cdot x$$

$$b = b + \eta \cdot error$$

So verschiebt sich die Entscheidungsgrenze Schritt für Schritt, bis die AND-Punkte möglichst sauber getrennt sind.
        """
    )

if st.session_state.perceptron_is_animating:
    if st.session_state.perceptron_current_step < max_step:
        time.sleep(0.18)
        st.session_state.perceptron_current_step += 1
        st.rerun()
    else:
        st.session_state.perceptron_is_animating = False
