import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Seite konfigurieren
st.set_page_config(page_title="Neuronales Netz - Binary AND", layout="wide")
st.title("Neuronales Netz: Binary AND Operation")

# Sidebar für Parameter
st.sidebar.header("Netzwerk Parameter")
st.sidebar.write("Binäre AND Operation: output = input1 AND input2")

# Input-Werte
input1 = st.sidebar.slider("Input 1", 0, 1, 0, step=1)
input2 = st.sidebar.slider("Input 2", 0, 1, 0, step=1)

# Gewichte initialisieren (trainiert für AND-Operation)
if "weights_hidden" not in st.session_state:
    st.session_state.weights_hidden = np.array([[1.5, 1.5], [1.5, 1.5]])
    st.session_state.bias_hidden = np.array([-2.25, -2.25])
    st.session_state.weights_output = np.array([1.0, 1.0])
    st.session_state.bias_output = -0.5

if "manual_mode" not in st.session_state:
    st.session_state.manual_mode = False

# Simulation state
if "sim_step" not in st.session_state:
    st.session_state.sim_step = 0
if "sim_max_step" not in st.session_state:
    st.session_state.sim_max_step = 4

# Manueller Modus für Gewichte
st.sidebar.subheader("Gewichte anpassen")
manual_mode = st.sidebar.checkbox("Gewichte manuell anpassen", value=st.session_state.manual_mode)
st.session_state.manual_mode = manual_mode

if manual_mode:
    st.sidebar.write("**Hidden Layer Gewichte:**")
    st.session_state.weights_hidden[0, 0] = st.sidebar.slider(
        "W1→H1", -3.0, 3.0, st.session_state.weights_hidden[0, 0], step=0.1
    )
    st.session_state.weights_hidden[0, 1] = st.sidebar.slider(
        "W2→H1", -3.0, 3.0, st.session_state.weights_hidden[0, 1], step=0.1
    )
    st.session_state.weights_hidden[1, 0] = st.sidebar.slider(
        "W1→H2", -3.0, 3.0, st.session_state.weights_hidden[1, 0], step=0.1
    )
    st.session_state.weights_hidden[1, 1] = st.sidebar.slider(
        "W2→H2", -3.0, 3.0, st.session_state.weights_hidden[1, 1], step=0.1
    )

    st.sidebar.write("**Bias Hidden Layer:**")
    st.session_state.bias_hidden[0] = st.sidebar.slider(
        "B_H1", -2.0, 2.0, st.session_state.bias_hidden[0], step=0.1
    )
    st.session_state.bias_hidden[1] = st.sidebar.slider(
        "B_H2", -2.0, 2.0, st.session_state.bias_hidden[1], step=0.1
    )

    st.sidebar.write("**Output Layer Gewichte:**")
    st.session_state.weights_output[0] = st.sidebar.slider(
        "H1→Out", -2.0, 2.0, st.session_state.weights_output[0], step=0.1
    )
    st.session_state.weights_output[1] = st.sidebar.slider(
        "H2→Out", -2.0, 2.0, st.session_state.weights_output[1], step=0.1
    )
    st.sidebar.write("**Bias Output Layer:**")
    st.session_state.bias_output = st.sidebar.slider(
        "B_Out", -2.0, 2.0, st.session_state.bias_output, step=0.1
    )

# Simulation Controls
st.sidebar.subheader("Simulation")
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
st.session_state.dark_mode = st.sidebar.checkbox("Dark mode", value=st.session_state.dark_mode)

sim_step = st.sidebar.slider(
    "Simulation Schritt", 0, st.session_state.sim_max_step, st.session_state.sim_step
)
st.session_state.sim_step = sim_step

sim_back = st.sidebar.button("Schritt zurück")
sim_forward = st.sidebar.button("Schritt vorwärts")
if sim_back:
    st.session_state.sim_step = max(0, st.session_state.sim_step - 1)
if sim_forward:
    st.session_state.sim_step = min(st.session_state.sim_max_step, st.session_state.sim_step + 1)


# Aktivierungsfunktion (Sigmoid)
def sigmoid(x):
    return 1 / (1 + np.exp(-np.clip(x, -500, 500)))


def relu(x):
    return np.maximum(0, x)


# Forward Pass
inputs = np.array([input1, input2])

# Hidden Layer
hidden_raw = np.dot(st.session_state.weights_hidden, inputs) + st.session_state.bias_hidden
hidden_activation = sigmoid(hidden_raw)

# Output Layer
output_raw = (
    np.dot(st.session_state.weights_output, hidden_activation) + st.session_state.bias_output
)
output_activation = sigmoid(output_raw)

# Expected output für AND
expected_output = input1 & input2

# Hauptlayout mit zwei Spalten
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Netzwerk Visualisierung")

    # Farben basierend auf Aktivierung (0-1)
    def get_color(activation):
        if activation < 0.3:
            return "rgba(46, 134, 171, 0.8)"  # Blau
        elif activation < 0.7:
            return "rgba(162, 59, 114, 0.8)"  # Violett
        else:
            return "rgba(241, 143, 1, 0.8)"  # Orange

    # Netzwerk mit Plotly zeichnen
    def build_network_figure():
        fig_local = go.Figure()
        # Layer Positionen
        layer_x = [1, 5, 9]
        input_y = [3, 1]
        hidden_y = [3.5, 0.5]
        output_y = [2]

        # Swimlanes (Hintergrund)
        swimlane_colors = {
            True: [
                "rgba(255,255,255,0.02)",
                "rgba(255,255,255,0.01)",
                "rgba(255,255,255,0.02)",
            ],
            False: [
                "rgba(255,255,255,0.06)",
                "rgba(255,255,255,0.04)",
                "rgba(255,255,255,0.06)",
            ],
        }
        is_dark = st.session_state.dark_mode
        swim_colors = swimlane_colors[is_dark]

        # swimlane hintergründe
        fig_local.add_shape(
            type="rect",
            x0=0.5,
            x1=3,
            y0=0,
            y1=4.5,
            fillcolor=swim_colors[0],
            line_width=0,
        )
        fig_local.add_shape(
            type="rect",
            x0=3,
            x1=7,
            y0=0,
            y1=4.5,
            fillcolor=swim_colors[1],
            line_width=0,
        )
        fig_local.add_shape(
            type="rect",
            x0=7,
            x1=10.5,
            y0=0,
            y1=4.5,
            fillcolor=swim_colors[2],
            line_width=0,
        )

        # Input Neuronen
        for _i, (y, val) in enumerate(zip(input_y, [input1, input2], strict=False)):
            highlight = st.session_state.sim_step == 0
            marker_line = (
                {"color": "yellow", "width": 4} if highlight else {"color": "black", "width": 2}
            )
            size = 48 if highlight else 35
            fig_local.add_trace(
                go.Scatter(
                    x=[layer_x[0]],
                    y=[y],
                    mode="markers+text",
                    marker={"size": size, "color": get_color(val), "line": marker_line},
                    text=[f"{int(val)}"],
                    textposition="middle center",
                    textfont={"color": "white", "size": 14},
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

        # Hidden Neuronen
        for _i, (y, val) in enumerate(zip(hidden_y, hidden_activation, strict=False)):
            highlight = st.session_state.sim_step == 2
            marker_line = (
                {"color": "yellow", "width": 4} if highlight else {"color": "black", "width": 2}
            )
            size = 48 if highlight else 35
            fig_local.add_trace(
                go.Scatter(
                    x=[layer_x[1]],
                    y=[y],
                    mode="markers+text",
                    marker={"size": size, "color": get_color(val), "line": marker_line},
                    text=[f"{val:.2f}"],
                    textposition="middle center",
                    textfont={"color": "white", "size": 12},
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

        # Output Neuron
        highlight_out = st.session_state.sim_step == 4
        marker_line = (
            {"color": "yellow", "width": 4} if highlight_out else {"color": "black", "width": 3}
        )
        size = 56 if highlight_out else 40
        fig_local.add_trace(
            go.Scatter(
                x=[layer_x[2]],
                y=[output_y[0]],
                mode="markers+text",
                marker={
                    "size": size,
                    "color": get_color(output_activation),
                    "line": marker_line,
                },
                text=[f"{output_activation:.3f}"],
                textposition="middle center",
                textfont={"color": "white", "size": 12},
                hoverinfo="skip",
                showlegend=False,
            )
        )

        # Verbindungen Input -> Hidden
        for i in range(2):
            for j in range(2):
                weight = st.session_state.weights_hidden[j, i]
                color_line = "red" if weight < 0 else "green"
                x1, y1 = layer_x[0], input_y[i]
                x2, y2 = layer_x[1], hidden_y[j]

                # highlight edges on step 1
                highlight_e = st.session_state.sim_step == 1
                line_width = abs(weight) * 3.0 if highlight_e else abs(weight) * 2
                line_color = "yellow" if highlight_e else color_line
                fig_local.add_trace(
                    go.Scatter(
                        x=[x1, x2],
                        y=[y1, y2],
                        mode="lines",
                        line={
                            "color": line_color,
                            "width": line_width,
                            "dash": "solid",
                        },
                        hoverinfo="skip",
                        showlegend=False,
                    )
                )

                # Gewicht-Label
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                if st.session_state.sim_step == 1:
                    contrib = weight * (input1 if i == 0 else input2)
                    label = f"c: {contrib:.2f}"
                else:
                    label = f"{weight:.2f}"

                fig_local.add_annotation(
                    x=mid_x,
                    y=mid_y,
                    text=label,
                    showarrow=False,
                    bgcolor="yellow",
                    bordercolor="black",
                    borderwidth=1,
                    font={"size": 8},
                )

        # Verbindungen Hidden -> Output
        for i in range(2):
            weight = st.session_state.weights_output[i]
            color_line = "red" if weight < 0 else "green"
            x1, y1 = layer_x[1], hidden_y[i]
            x2, y2 = layer_x[2], output_y[0]

            # highlight edges on step 3
            highlight_e = st.session_state.sim_step == 3
            line_width = abs(weight) * 3.5 if highlight_e else abs(weight) * 2.5
            line_color = "yellow" if highlight_e else color_line
            fig_local.add_trace(
                go.Scatter(
                    x=[x1, x2],
                    y=[y1, y2],
                    mode="lines",
                    line={"color": line_color, "width": line_width, "dash": "solid"},
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            if st.session_state.sim_step == 3:
                contrib = weight * hidden_activation[i]
                label = f"c: {contrib:.2f}"
            else:
                label = f"{weight:.2f}"

            fig_local.add_annotation(
                x=mid_x,
                y=mid_y,
                text=label,
                showarrow=False,
                bgcolor="yellow",
                bordercolor="black",
                borderwidth=1,
                font={"size": 8},
            )

        # Bias-Labels
        fig_local.add_annotation(
            x=layer_x[1],
            y=-0.5,
            text=f"Bias: {st.session_state.bias_hidden[0]:.2f}, {st.session_state.bias_hidden[1]:.2f}",
            showarrow=False,
            bgcolor="lightblue",
            bordercolor="black",
            borderwidth=1,
            font={"size": 9},
        )

        fig_local.add_annotation(
            x=layer_x[2],
            y=-0.5,
            text=f"Bias: {st.session_state.bias_output:.2f}",
            showarrow=False,
            bgcolor="lightblue",
            bordercolor="black",
            borderwidth=1,
            font={"size": 9},
        )

        # Legende hinzufügen
        legend_text = "<b>Farben:</b><br>🔵 Blau < 0.3<br>🟣 Violett 0.3-0.7<br>🟠 Orange > 0.7<br><br><b>Linien:</b><br>🟢 Grün = positive<br>🔴 Rot = negative"
        fig_local.add_annotation(
            x=-0.2,
            y=4.5,
            text=legend_text,
            showarrow=False,
            bgcolor=("rgba(255,255,255,0.9)" if not is_dark else "rgba(30,30,30,0.8)"),
            bordercolor="gray",
            borderwidth=1,
            font={"size": 9},
            align="left",
        )

        # Swimlane labels
        fig_local.add_annotation(
            x=2.0,
            y=4.8,
            text="Input Layer",
            showarrow=False,
            font={"size": 12, "color": ("white" if is_dark else "black")},
        )
        fig_local.add_annotation(
            x=5.0,
            y=4.8,
            text="Hidden Layer",
            showarrow=False,
            font={"size": 12, "color": ("white" if is_dark else "black")},
        )
        fig_local.add_annotation(
            x=8.8,
            y=4.8,
            text="Output Layer",
            showarrow=False,
            font={"size": 12, "color": ("white" if is_dark else "black")},
        )

        # Dark mode template
        template = "plotly_dark" if st.session_state.dark_mode else "plotly_white"
        fig_local.update_layout(
            showlegend=False,
            hovermode="closest",
            xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            yaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
            template=template,
            plot_bgcolor="rgba(0,0,0,0)" if st.session_state.dark_mode else "white",
            width=1000,
            height=600,
            margin={"l": 50, "r": 50, "t": 50, "b": 50},
        )
        return fig_local

    # render chart, möglicherweise Auto-Play mit Updates
    placeholder = st.empty()
    fig = build_network_figure()
    placeholder.plotly_chart(fig, width="stretch")

    # Step description
    step_texts = {
        0: "Inputs ausgewählt — bereit, Transfer zu Hidden Layer zu zeigen.",
        1: "Input → Hidden: wir zeigen Beiträge (Gewicht × Input) für jede Verbindung.",
        2: "Hidden Aktivierung: Sigmoid-Anzeige der H-Outputs.",
        3: "Hidden → Output: Beiträge (Gewicht × Hidden-Aktivierung).",
        4: "Output: Berechnung des Outputs und Vorhersage (0/1).",
    }
    st.info(step_texts.get(st.session_state.sim_step, ""))

with col2:
    st.subheader("Berechnung")

    # Detaillierte Berechnung anzeigen
    st.write("**Eingaben:**")
    st.write(f"Input 1: {input1}")
    st.write(f"Input 2: {input2}")

    st.divider()

    st.write("**Hidden Layer Berechnung:**")
    if st.session_state.sim_step == 1:
        st.write("(Simulation: Beiträge Input→Hidden)")
    for i in range(2):
        w1, w2 = st.session_state.weights_hidden[i]
        b = st.session_state.bias_hidden[i]
        raw = w1 * input1 + w2 * input2 + b
        activated = hidden_activation[i]
        st.write(f"**H{i+1}:**")
        # symbolic formula
        st.latex(r"z = w_1 x_1 + w_2 x_2 + b")
        # numeric substitution
        st.latex(
            rf"z_{{H{i+1}}} = {w1:.2f}\cdot {input1} + {w2:.2f}\cdot {input2} + {b:.2f} = {raw:.3f}"
        )
        st.latex(rf"\sigma(z) = \frac{{1}}{{1+e^{{-z}}}} = {activated:.4f}")
        if st.session_state.sim_step == 1:
            contrib1 = st.session_state.weights_hidden[i, 0] * input1
            contrib2 = st.session_state.weights_hidden[i, 1] * input2
            st.latex(rf"w_{{1}}x_{{1}} = {contrib1:.3f},\quad w_{{2}}x_{{2}} = {contrib2:.3f}")

    st.divider()

    # Inspect connections and neurons
    st.subheader("Inspektion: Schicht / Gewicht / Neuron")
    inspect_options = [
        "H1",
        "H2",
        "Output",
        "W1→H1",
        "W2→H1",
        "W1→H2",
        "W2→H2",
        "H1→Out",
        "H2→Out",
    ]
    inspect_sel = st.selectbox(
        "Wähle ein Neuron oder eine Verbindung zum Untersuchen:", inspect_options
    )

    def show_weight_detail(weight, x_value, label, z_target=None):
        contrib = weight * x_value
        st.latex(rf"{label}: c = w \cdot x = {weight:.3f}\cdot {x_value} = {contrib:.4f}")
        if z_target is not None and abs(z_target) > 1e-9:
            pct = 100 * contrib / z_target
            st.latex(rf"\text{{Anteil an }}z: {pct:.2f}\%")
        else:
            st.write("Anteil an z: - (z = 0)")

    # show details depending on selection
    with st.expander("Detaillierte Rechnungen anzeigen", expanded=True):
        if inspect_sel in ["W1→H1", "W2→H1", "W1→H2", "W2→H2"]:
            # parse index
            # map labels to indices
            map_hidden = {
                "W1→H1": (0, 0),
                "W2→H1": (1, 0),
                "W1→H2": (0, 1),
                "W2→H2": (1, 1),
            }
            i_input, j_hidden = map_hidden[inspect_sel]
            weight = st.session_state.weights_hidden[j_hidden, i_input]
            x_val = input1 if i_input == 0 else input2
            z_target = (
                np.dot(st.session_state.weights_hidden[j_hidden], inputs)
                + st.session_state.bias_hidden[j_hidden]
            )
            st.write(f"Untersuchung: {inspect_sel}")
            show_weight_detail(weight, x_val, inspect_sel, z_target)
            st.latex(rf"z_{{H{j_hidden+1}}} = {z_target:.4f}")

        elif inspect_sel in ["H1", "H2"]:
            idx = 0 if inspect_sel == "H1" else 1
            w1, w2 = st.session_state.weights_hidden[idx]
            b = st.session_state.bias_hidden[idx]
            z = w1 * input1 + w2 * input2 + b
            st.latex(
                rf"z_{{{inspect_sel}}} = {w1:.3f}\cdot {input1} + {w2:.3f}\cdot {input2} + {b:.3f} = {z:.4f}"
            )
            st.latex(rf"\sigma(z_{{{inspect_sel}}}) = {hidden_activation[idx]:.4f}")
            st.latex(rf"\text{{Beiträge: }} w_1x_1 = {w1*input1:.4f},\; w_2x_2 = {w2*input2:.4f}")

        elif inspect_sel in ["H1→Out", "H2→Out"]:
            idx = 0 if inspect_sel == "H1→Out" else 1
            weight = st.session_state.weights_output[idx]
            hval = hidden_activation[idx]
            z_out = (
                np.dot(st.session_state.weights_output, hidden_activation)
                + st.session_state.bias_output
            )
            st.write(f"Untersuchung: {inspect_sel}")
            show_weight_detail(weight, hval, inspect_sel, z_out)
            st.latex(rf"z_{{Out}} = {z_out:.4f}")

        elif inspect_sel == "Output":
            w1, w2 = st.session_state.weights_output
            b = st.session_state.bias_output
            z = w1 * hidden_activation[0] + w2 * hidden_activation[1] + b
            st.latex(
                rf"z_{{Out}} = {w1:.3f}\cdot {hidden_activation[0]:.4f} + {w2:.3f}\cdot {hidden_activation[1]:.4f} + {b:.3f} = {z:.4f}"
            )
            st.latex(rf"\sigma(z_{{Out}}) = {output_activation:.4f}")
            st.latex(
                rf"\text{{Beiträge: }} h_1w_1 = {hidden_activation[0]*w1:.4f},\; h_2w_2 = {hidden_activation[1]*w2:.4f}"
            )

    st.write("**Output Layer Berechnung:**")
    w1, w2 = st.session_state.weights_output
    b = st.session_state.bias_output
    raw = w1 * hidden_activation[0] + w2 * hidden_activation[1] + b
    st.latex(r"z = w_1 h_1 + w_2 h_2 + b")
    st.latex(
        rf"z = {w1:.2f}\cdot {hidden_activation[0]:.4f} + {w2:.2f}\cdot {hidden_activation[1]:.4f} + {b:.2f} = {raw:.4f}"
    )
    st.latex(rf"Output = \sigma(z) = {output_activation:.4f}")
    if st.session_state.sim_step == 3:
        st.write("(Simulation: Beiträge Hidden→Output)")
        st.latex(
            rf"h_{{1}}w_{{1}} = {hidden_activation[0]*w1:.3f},\quad h_{{2}}w_{{2}} = {hidden_activation[1]*w2:.3f}"
        )

    st.divider()

    # Ergebnis
    st.write("**Ergebnis:**")
    predicted_class = 1 if output_activation > 0.5 else 0

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.metric("Vorhergesagt", predicted_class, delta=None, delta_color="off")
    with col_res2:
        st.metric("Erwartet", expected_output, delta=None, delta_color="off")

    # Fehler
    error = abs(output_activation - expected_output)
    if error < 0.1:
        st.success(f"Korrekt! Error: {error:.4f}")
    elif error < 0.3:
        st.warning(f"Unsicher. Error: {error:.4f}")
    else:
        st.error(f"Falsch! Error: {error:.4f}")

st.divider()

# Truth Table anzeigen
st.subheader("Truth Table - Binary AND")

col1, col2 = st.columns(2)

with col1:
    st.write("**Netzwerk Output:**")
    truth_data = []
    for i in [0, 1]:
        for j in [0, 1]:
            inp = np.array([i, j])
            h_raw = np.dot(st.session_state.weights_hidden, inp) + st.session_state.bias_hidden
            h_act = sigmoid(h_raw)
            o_raw = np.dot(st.session_state.weights_output, h_act) + st.session_state.bias_output
            o_act = sigmoid(o_raw)
            pred = 1 if o_act > 0.5 else 0
            truth_data.append(
                {
                    "Input 1": i,
                    "Input 2": j,
                    "Output (Raw)": f"{o_act:.4f}",
                    "Output (Pred)": pred,
                }
            )

    df = pd.DataFrame(truth_data)
    st.dataframe(df, width="stretch")

with col2:
    st.write("**Expected (Binary AND):**")
    expected_data = []
    for i in [0, 1]:
        for j in [0, 1]:
            expected_data.append({"Input 1": i, "Input 2": j, "Output": i & j})
    df_expected = pd.DataFrame(expected_data)
    st.dataframe(df_expected, width="stretch")

st.divider()

st.subheader("Aktivierungsfunktion")
st.latex(r"\sigma(x) = \frac{1}{1 + e^{-x}}")
st.write(
    "Das Output Neuron leuchtet intensiv auf (orange), wenn es aktiviert ist (>0.5), und dunkel (blau), wenn es inaktiv ist (<0.3)."
)


st.subheader("Anleitung")
st.markdown(
    """
    - Schritt 1: Inputs setzen
    Wähle links in der Sidebar:
    - **Input 1**
    - **Input 2**

    Beide Inputs sind binär (0 oder 1), genau wie bei der AND-Logik.

    - Schritt 2: Simulation Schritt für Schritt
    Mit dem **Simulation-Schieberegler** kannst du durch die Berechnung gehen:

    | Schritt |              Bedeutung                    |
    |---------|-------------------------------------------|
    |    0    | Inputs werden gesetzt                     |
    |    1    | Beiträge Input → Hidden (Gewicht x Input) |
    |    2    | Aktivierung der Hidden-Neuronen           |
    |    3    | Beiträge Hidden → Output                  |
    |    4    | Finaler Output                            |

    Die **gelben Markierungen** zeigen immer,
    welcher Teil des Netzwerks gerade aktiv ist.

    - Schritt 3: Gewichte untersuchen
    Rechts kannst du:
    - einzelne **Neuronen**
    - oder **Verbindungen (Gewichte)**

    auswählen und siehst:
    - mathematische Formeln
    - konkrete Zahlen
    - den Beitrag zum Gesamtergebnis
    """
)

# --------------------------------------------------
# Explanation
# --------------------------------------------------
with st.expander("Erklärung - Neuronales Netz", expanded=False):
    st.markdown("---")
    st.markdown("## Was ist ein neuronales Netz?")

    st.markdown(
        """
        Ein neuronales Netz ist ein **mathematisches Modell**, das lose
        an das menschliche Gehirn angelehnt ist.

        Es besteht aus:
        - **Neuronen** (Recheneinheiten)
        - **Gewichten** (Einflussstärke)
        - **Bias** (Verschiebung)
        - **Aktivierungsfunktionen**

        Jedes Neuron berechnet:
        """
    )

    st.latex(r"z = \sum w_i x_i + b")
    st.latex(r"\text{Output} = \sigma(z)")

    st.markdown(
        """
        Die Aktivierungsfunktion (hier **Sigmoid**) sorgt dafür,
        dass der Output zwischen **0 und 1** liegt.
        """
    )

    st.markdown("---")
    st.markdown("## Warum ein Hidden Layer für AND?")

    st.markdown(
        """
        Theoretisch kann AND auch mit **einem einzelnen Perceptron**
        gelöst werden.

        **Warum dann ein Hidden Layer?**

        Diese Seite ist didaktisch aufgebaut, um:
        - echte neuronale Netze zu zeigen
        - spätere Erweiterungen (z.B. XOR) zu ermöglichen
        - den Datenfluss besser sichtbar zu machen

        Der Hidden Layer zeigt:
        - wie Zwischenrepräsentationen entstehen
        - wie mehrere Neuronen gemeinsam entscheiden
        """
    )

    st.markdown("---")
    st.markdown("## Farben & Linien verstehen")

    st.markdown(
        """
        ### Neuronenfarben
        Die Farbe eines Neurons zeigt seine **Aktivierung**:

        - 🔵 **Blau** → kaum aktiv (≈ 0)
        - 🟣 **Violett** → mittel aktiv
        - 🟠 **Orange** → stark aktiv (≈ 1)

        ---
        ### Verbindungen (Gewichte)
        - 🟢 **Grün** → positives Gewicht
        - 🔴 **Rot** → negatives Gewicht
        - **Linienstärke** → Einflussstärke

        In bestimmten Simulationsschritten werden zusätzlich
        die **Beiträge (Gewicht × Aktivierung)** angezeigt.
        """
    )

    st.markdown("---")
    st.markdown("## Output & Entscheidung")

    st.markdown(
        """
        Das Output-Neuron berechnet einen Wert zwischen **0 und 1**.

        **Entscheidungsregel:**
        - Output > 0.5 → **1** (TRUE)
        - Output ≤ 0.5 → **0** (FALSE)

        Das entspricht exakt der **AND-Wahrheitstabelle**,
        die unten auf der Seite angezeigt wird.
        """
    )

    st.markdown("---")
    st.markdown("## Wie lernt das Netz? (Training)")

    st.markdown(
        """
        Diese Visualisierung zeigt ein **bereits trainiertes** Netz.
        Aber wie kommt man zu diesen perfekten Gewichten?

        ### Training mit Backpropagation

        1. **Forward Pass** - Eingabe durch das Netz propagieren
        2. **Fehler berechnen** - Differenz zwischen Output und Zielwert
        3. **Backward Pass** - Fehler rückwärts durch das Netz propagieren
        4. **Gewichte anpassen** - Mit Gradient Descent optimieren
        5. **Wiederholen** - Bis Fehler minimal ist

        **Loss-Funktion (für binäre Klassifikation):**
        """
    )
    st.latex(r"L = -\sum [y \log(\hat{y}) + (1-y) \log(1-\hat{y})]")

    st.markdown(
        """
        Diese **Binary Cross-Entropy** Loss-Funktion misst,
        wie gut die Vorhersagen mit den tatsächlichen Werten übereinstimmen.
        """
    )

    st.markdown("---")
    st.markdown("## Praktische Tipps")

    tip_col1, tip_col2 = st.columns(2)

    with tip_col1:
        st.markdown("### 💡 Experimentieren")
        st.markdown(
            """
            **Mit manuellen Gewichten:**
            - Aktiviere "Gewichte manuell anpassen"
            - Verändere einzelne Gewichte
            - Beobachte die Auswirkung auf den Output

            **Fragen zum Testen:**
            - Was passiert bei allen Gewichten = 0?
            - Welche Gewichte sind am wichtigsten?
            - Kann man Hidden Layer weglassen?
            """
        )

    with tip_col2:
        st.markdown("### 🎯 Verständniskontrolle")
        st.markdown(
            """
            **Teste dein Verständnis:**
            - Warum brauchen wir einen Hidden Layer?
            - Was macht die Sigmoid-Funktion?
            - Warum sind die Bias-Werte negativ?

            **Experiment:**
            - Setze alle Hidden-Bias auf 0
            - Was passiert mit der AND-Operation?
            """
        )

    st.markdown("---")
    st.markdown("## Von AND zu komplexeren Problemen")

    st.markdown(
        """
        ### Warum ist AND so einfach?
        AND ist **linear trennbar** - ein einzelnes Perceptron würde genügen.
        Der Hidden Layer zeigt aber das **Prinzip** für komplexere Probleme.

        ### XOR - Der nächste Schritt
        **XOR** (Exclusive OR) ist **nicht linear trennbar**:
        - (0,0) → 0
        - (0,1) → 1
        - (1,0) → 1
        - (1,1) → 0

        Ein einlagiges Netz **kann XOR nicht lösen**!
        Mit einem Hidden Layer wird es möglich - genau wie hier gezeigt.

        ### Real-World Applications
        Moderne neuronale Netze nutzen dasselbe Prinzip, nur mit:
        - **Hunderten von Layern** (Deep Learning)
        - **Tausenden von Neuronen** pro Layer
        - **Millionen von Parametern**

        Anwendungen:
        - Bilderkennung (CNNs)
        - Sprachverarbeitung (RNNs, Transformers)
        - Autonomes Fahren
        - Medizinische Diagnose
        """
    )
