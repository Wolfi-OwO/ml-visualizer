import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.neural_network import (
    create_network_params,
    evaluate_and_truth_table,
    forward_pass,
    params_from_dict,
    params_to_dict,
    snapshot_to_params,
    train_and_network,
)

DEFAULT_TRAINING_CONFIG = {
    "learning_rate": 0.3,
    "epochs": 300,
    "seed": 1,
}

st.title("Neuronales Netz: Binary AND Operation")
st.caption("Das Netz kann jetzt trainieren, Snapshots laden und auf kleinere Layouts reagieren.")


def store_params(params) -> None:
    st.session_state.nn_params = params_to_dict(params)


def load_params():
    return params_from_dict(st.session_state.nn_params)


def reset_network(seed: int) -> None:
    params = create_network_params(seed=seed)
    evaluation = evaluate_and_truth_table(params)
    store_params(params)
    st.session_state.nn_history = [
        {
            **params_to_dict(params),
            "epoch": 0,
            "loss": evaluation["loss"],
            "accuracy": evaluation["accuracy"],
        }
    ]
    st.session_state.nn_snapshot_index = 0
    st.session_state.nn_loaded_snapshot = 0


if "nn_params" not in st.session_state or "nn_history" not in st.session_state:
    reset_network(seed=1)
if "nn_manual_mode" not in st.session_state:
    st.session_state.nn_manual_mode = False
if "nn_dark_mode" not in st.session_state:
    st.session_state.nn_dark_mode = True
if "nn_sim_step" not in st.session_state:
    st.session_state.nn_sim_step = 0
if "nn_training_config" not in st.session_state:
    st.session_state.nn_training_config = DEFAULT_TRAINING_CONFIG.copy()

st.sidebar.header("Netzwerk Parameter")
st.sidebar.write("Binary AND: output = input1 AND input2")
input1 = st.sidebar.slider("Input 1", 0, 1, 0, step=1)
input2 = st.sidebar.slider("Input 2", 0, 1, 0, step=1)

st.sidebar.subheader("Training")
with st.sidebar.form("nn_training_controls"):
    learning_rate = st.slider(
        "Lernrate",
        0.05,
        1.0,
        float(st.session_state.nn_training_config["learning_rate"]),
        0.05,
    )
    epochs = st.slider(
        "Epochen",
        50,
        600,
        int(st.session_state.nn_training_config["epochs"]),
        25,
    )
    seed = st.number_input(
        "Seed",
        min_value=0,
        max_value=9999,
        value=int(st.session_state.nn_training_config["seed"]),
        step=1,
    )
    train_button = st.form_submit_button("Netz trainieren", type="primary")
    reset_button = st.form_submit_button("Neu initialisieren")
st.sidebar.caption("Das Training startet immer mit den aktuellen Gewichten.")

if train_button or reset_button:
    st.session_state.nn_training_config = {
        "learning_rate": float(learning_rate),
        "epochs": int(epochs),
        "seed": int(seed),
    }

if reset_button:
    reset_network(int(seed))

if train_button:
    trained_params, history = train_and_network(
        initial_params=load_params(),
        learning_rate=learning_rate,
        epochs=epochs,
        seed=int(seed),
    )
    store_params(trained_params)
    st.session_state.nn_history = history
    st.session_state.nn_snapshot_index = len(history) - 1
    st.session_state.nn_loaded_snapshot = len(history) - 1

history = st.session_state.nn_history
max_snapshot = len(history) - 1
snapshot_default = min(st.session_state.nn_snapshot_index, max_snapshot)
if max_snapshot > 0:
    snapshot_index = st.sidebar.slider("Trainings-Snapshot", 0, max_snapshot, snapshot_default)
else:
    snapshot_index = 0
    st.sidebar.caption(
        "Noch kein Trainingsverlauf vorhanden. Trainiere das Netz, um Snapshots zu sehen."
    )
st.session_state.nn_snapshot_index = snapshot_index

manual_mode = st.sidebar.checkbox(
    "Gewichte manuell anpassen",
    value=st.session_state.nn_manual_mode,
)
st.session_state.nn_manual_mode = manual_mode

if not manual_mode and st.session_state.nn_loaded_snapshot != snapshot_index:
    store_params(snapshot_to_params(history[snapshot_index]))
    st.session_state.nn_loaded_snapshot = snapshot_index

params = load_params()

if manual_mode:
    st.sidebar.subheader("Gewichte")
    with st.sidebar.form("nn_manual_weights"):
        weight_h1_i1 = st.slider("W1->H1", -4.0, 4.0, float(params.weights_hidden[0, 0]), 0.1)
        weight_h1_i2 = st.slider("W2->H1", -4.0, 4.0, float(params.weights_hidden[0, 1]), 0.1)
        weight_h2_i1 = st.slider("W1->H2", -4.0, 4.0, float(params.weights_hidden[1, 0]), 0.1)
        weight_h2_i2 = st.slider("W2->H2", -4.0, 4.0, float(params.weights_hidden[1, 1]), 0.1)
        bias_h1 = st.slider("Bias H1", -3.0, 3.0, float(params.bias_hidden[0]), 0.1)
        bias_h2 = st.slider("Bias H2", -3.0, 3.0, float(params.bias_hidden[1]), 0.1)
        weight_out_h1 = st.slider("H1->Out", -4.0, 4.0, float(params.weights_output[0]), 0.1)
        weight_out_h2 = st.slider("H2->Out", -4.0, 4.0, float(params.weights_output[1]), 0.1)
        bias_out = st.slider("Bias Out", -3.0, 3.0, float(params.bias_output), 0.1)
        apply_manual_weights = st.form_submit_button("Gewichte anwenden")

    if apply_manual_weights:
        params.weights_hidden[0, 0] = weight_h1_i1
        params.weights_hidden[0, 1] = weight_h1_i2
        params.weights_hidden[1, 0] = weight_h2_i1
        params.weights_hidden[1, 1] = weight_h2_i2
        params.bias_hidden[0] = bias_h1
        params.bias_hidden[1] = bias_h2
        params.weights_output[0] = weight_out_h1
        params.weights_output[1] = weight_out_h2
        params.bias_output = bias_out
        store_params(params)
        st.session_state.nn_loaded_snapshot = -1
        params = load_params()

dark_mode = st.sidebar.checkbox("Dark mode", value=st.session_state.nn_dark_mode)
st.session_state.nn_dark_mode = dark_mode
sim_step = st.sidebar.slider("Signalfluss", 0, 4, st.session_state.nn_sim_step)
st.session_state.nn_sim_step = sim_step

params = load_params()
inputs = np.array([input1, input2], dtype=float)
forward = forward_pass(inputs, params)
hidden_raw = np.asarray(forward["hidden_raw"], dtype=float)
hidden_activation = np.asarray(forward["hidden_activation"], dtype=float)
output_raw = float(forward["output_raw"])
output_activation = float(forward["output_activation"])
expected_output = input1 & input2
predicted_output = int(output_activation >= 0.5)
truth_table = evaluate_and_truth_table(params)


def activation_color(value: float) -> str:
    if value < 0.3:
        return "#2e86ab"
    if value < 0.7:
        return "#a23b72"
    return "#f18f01"


def edge_color(weight: float, highlighted: bool) -> str:
    if highlighted:
        return "#facc15"
    return "#22c55e" if weight >= 0 else "#ef4444"


def build_network_figure() -> go.Figure:
    fig = go.Figure()
    x_positions = [0.0, 1.0, 2.0]
    input_y = [0.8, 0.2]
    hidden_y = [0.85, 0.15]
    output_y = [0.5]

    for input_index, start_y in enumerate(input_y):
        for hidden_index, end_y in enumerate(hidden_y):
            weight = float(params.weights_hidden[hidden_index, input_index])
            contribution = weight * inputs[input_index]
            highlighted = sim_step == 1
            fig.add_trace(
                go.Scatter(
                    x=[x_positions[0], x_positions[1]],
                    y=[start_y, end_y],
                    mode="lines",
                    line={
                        "color": edge_color(weight, highlighted),
                        "width": max(2.0, 2.5 + abs(weight) * 1.6),
                    },
                    hoverinfo="skip",
                    showlegend=False,
                )
            )
            fig.add_annotation(
                x=(x_positions[0] + x_positions[1]) / 2,
                y=(start_y + end_y) / 2,
                text=f"{contribution:.2f}" if highlighted else f"{weight:.2f}",
                showarrow=False,
                font={"size": 11},
                bgcolor="rgba(255,255,255,0.85)" if not dark_mode else "rgba(17,24,39,0.85)",
                bordercolor="rgba(148,163,184,0.7)",
                borderwidth=1,
            )

    for hidden_index, start_y in enumerate(hidden_y):
        weight = float(params.weights_output[hidden_index])
        contribution = weight * hidden_activation[hidden_index]
        highlighted = sim_step == 3
        fig.add_trace(
            go.Scatter(
                x=[x_positions[1], x_positions[2]],
                y=[start_y, output_y[0]],
                mode="lines",
                line={
                    "color": edge_color(weight, highlighted),
                    "width": max(2.0, 2.5 + abs(weight) * 1.8),
                },
                hoverinfo="skip",
                showlegend=False,
            )
        )
        fig.add_annotation(
            x=(x_positions[1] + x_positions[2]) / 2,
            y=(start_y + output_y[0]) / 2,
            text=f"{contribution:.2f}" if highlighted else f"{weight:.2f}",
            showarrow=False,
            font={"size": 11},
            bgcolor="rgba(255,255,255,0.85)" if not dark_mode else "rgba(17,24,39,0.85)",
            bordercolor="rgba(148,163,184,0.7)",
            borderwidth=1,
        )

    for y_value, node_value in zip(input_y, inputs, strict=False):
        fig.add_trace(
            go.Scatter(
                x=[x_positions[0]],
                y=[y_value],
                mode="markers+text",
                marker={
                    "size": 40 if sim_step == 0 else 34,
                    "color": activation_color(float(node_value)),
                    "line": {"color": "#facc15" if sim_step == 0 else "#111827", "width": 3},
                },
                text=[f"{int(node_value)}"],
                textposition="middle center",
                textfont={"color": "white", "size": 13},
                hoverinfo="skip",
                showlegend=False,
            )
        )

    for node_index, (y_value, node_value) in enumerate(
        zip(hidden_y, hidden_activation, strict=False)
    ):
        fig.add_trace(
            go.Scatter(
                x=[x_positions[1]],
                y=[y_value],
                mode="markers+text",
                marker={
                    "size": 42 if sim_step == 2 else 36,
                    "color": activation_color(float(node_value)),
                    "line": {"color": "#facc15" if sim_step == 2 else "#111827", "width": 3},
                },
                text=[f"H{node_index + 1}<br>{node_value:.2f}"],
                textposition="middle center",
                textfont={"color": "white", "size": 11},
                hoverinfo="skip",
                showlegend=False,
            )
        )

    fig.add_trace(
        go.Scatter(
            x=[x_positions[2]],
            y=output_y,
            mode="markers+text",
            marker={
                "size": 50 if sim_step == 4 else 40,
                "color": activation_color(output_activation),
                "line": {"color": "#facc15" if sim_step == 4 else "#111827", "width": 3},
            },
            text=[f"Out<br>{output_activation:.2f}"],
            textposition="middle center",
            textfont={"color": "white", "size": 11},
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.add_annotation(x=0.0, y=1.05, text="Input", showarrow=False, font={"size": 13})
    fig.add_annotation(x=1.0, y=1.05, text="Hidden", showarrow=False, font={"size": 13})
    fig.add_annotation(x=2.0, y=1.05, text="Output", showarrow=False, font={"size": 13})
    fig.add_annotation(
        x=1.0,
        y=-0.06,
        text=f"Bias H: {params.bias_hidden[0]:.2f}, {params.bias_hidden[1]:.2f}",
        showarrow=False,
        font={"size": 11},
    )
    fig.add_annotation(
        x=2.0,
        y=-0.06,
        text=f"Bias Out: {params.bias_output:.2f}",
        showarrow=False,
        font={"size": 11},
    )

    fig.update_layout(
        template="plotly_dark" if dark_mode else "plotly_white",
        height=520,
        margin={"l": 20, "r": 20, "t": 30, "b": 20},
        autosize=True,
        showlegend=False,
        xaxis={"showgrid": False, "showticklabels": False, "zeroline": False, "range": [-0.3, 2.3]},
        yaxis={
            "showgrid": False,
            "showticklabels": False,
            "zeroline": False,
            "range": [-0.15, 1.15],
        },
    )
    return fig


def build_training_figure(history_rows: list[dict[str, object]]) -> go.Figure:
    history_df = pd.DataFrame(
        {
            "epoch": [row["epoch"] for row in history_rows],
            "loss": [row["loss"] for row in history_rows],
            "accuracy": [row["accuracy"] for row in history_rows],
        }
    )

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=history_df["epoch"],
            y=history_df["loss"],
            mode="lines",
            name="Loss",
            line={"color": "#2563eb", "width": 3},
        )
    )
    figure.add_trace(
        go.Scatter(
            x=history_df["epoch"],
            y=history_df["accuracy"],
            mode="lines",
            name="Accuracy",
            line={"color": "#f97316", "width": 3},
            yaxis="y2",
        )
    )

    if st.session_state.nn_loaded_snapshot >= 0:
        marker_epoch = history[snapshot_index]["epoch"]
        figure.add_vline(x=marker_epoch, line_dash="dash", line_color="#94a3b8")

    figure.update_layout(
        height=320,
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        autosize=True,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0.0},
        xaxis={"title": "Epoche"},
        yaxis={"title": "Loss"},
        yaxis2={"title": "Accuracy", "overlaying": "y", "side": "right", "range": [0, 1]},
    )
    return figure


step_texts = {
    0: "Inputs setzen",
    1: "Input -> Hidden: Gewichte und Beitraege",
    2: "Hidden Layer aktiviert sich",
    3: "Hidden -> Output: Beitraege werden aufsummiert",
    4: "Output und finale Vorhersage",
}

current_snapshot_label = (
    f"Epoche {history[snapshot_index]['epoch']}"
    if st.session_state.nn_loaded_snapshot >= 0
    else "Manuelle Gewichte"
)

visual_col, side_col = st.columns([2, 1], gap="large")

with visual_col:
    st.subheader("Netzwerk Visualisierung")
    st.plotly_chart(build_network_figure(), width="stretch")
    st.info(step_texts[sim_step])
    st.caption(
        "Gruen = positives Gewicht, Rot = negatives Gewicht, Orange/Violett/Blau = Aktivierung."
    )
    st.subheader("Trainingsverlauf")
    st.plotly_chart(build_training_figure(history), width="stretch")

with side_col:
    st.subheader("Aktueller Durchlauf")
    st.write(f"**Snapshot:** {current_snapshot_label}")
    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.metric("Vorhergesagt", predicted_output)
        st.metric("Loss", f"{truth_table['loss']:.4f}")
    with metric_col2:
        st.metric("Erwartet", expected_output)
        st.metric("Accuracy", f"{truth_table['accuracy'] * 100:.0f}%")

    hidden_df = pd.DataFrame(
        {
            "Neuron": ["H1", "H2"],
            "z": hidden_raw.round(4),
            "Aktivierung": hidden_activation.round(4),
        }
    )
    st.write("**Hidden Layer**")
    st.table(hidden_df)

    st.write("**Output Layer**")
    st.latex(
        rf"z_{{out}} = {params.weights_output[0]:.2f}\cdot {hidden_activation[0]:.3f} + "
        rf"{params.weights_output[1]:.2f}\cdot {hidden_activation[1]:.3f} + {params.bias_output:.2f}"
    )
    st.latex(rf"\sigma(z_{{out}}) = {output_activation:.4f}")
    st.write(f"AND({input1}, {input2}) = {expected_output} | Modell = {predicted_output}")

st.divider()
st.subheader("Truth Table - Binary AND")
truth_col, expected_col = st.columns(2, gap="large")
with truth_col:
    st.write("**Netzwerk Output**")
    st.table(pd.DataFrame(truth_table["rows"]))
with expected_col:
    st.write("**Erwartete Wahrheitstabelle**")
    expected_rows = [
        {"Input 1": 0, "Input 2": 0, "Expected": 0},
        {"Input 1": 0, "Input 2": 1, "Expected": 0},
        {"Input 1": 1, "Input 2": 0, "Expected": 0},
        {"Input 1": 1, "Input 2": 1, "Expected": 1},
    ]
    st.table(pd.DataFrame(expected_rows))

st.subheader("Anleitung")
st.markdown(
    """
    1. Setze die beiden binaeren Inputs in der Sidebar.
    2. Trainiere das Netz oder lade einen frueheren Snapshot.
    3. Nutze bei Bedarf den manuellen Modus, um einzelne Gewichte direkt zu veraendern.
    4. Der Signalfluss-Slider hebt den gerade erklaerten Teil des Netzes hervor.
    """
)

with st.expander("Wie das Training funktioniert", expanded=False):
    st.markdown(
        """
Das Training nutzt eine kleine 2-2-1 Architektur mit **Sigmoid**-Aktivierungen.
Trainiert wird auf der kompletten AND-Wahrheitstabelle per Batch-Gradient-Descent.

- Forward Pass: Eingaben werden durch Hidden- und Output-Layer propagiert.
- Loss: Binary Cross Entropy misst den Fehler der vier Trainingsbeispiele.
- Update: Backpropagation passt Gewichte und Biases schrittweise an.

Dadurch kannst du zwischen zufaellig initialisierten Gewichten, trainierten Snapshots
und manuellen Aenderungen hin- und herspringen.
        """
    )
