import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

DEFAULT_CONFIG = {
    "x0": 8.0,
    "lr": 0.005,
    "iterations": 15,
}

st.title("Gradient Descent Visualizer")
st.caption("Beobachte, wie sich der Startwert mit jedem Schritt in Richtung Minimum bewegt.")


def f(x):
    return 0.5 * x**2


def df(x):
    return x


@st.cache_data(show_spinner=False)
def build_history(start_x: float, learning_rate: float, iteration_count: int) -> dict[str, object]:
    x = float(start_x)
    x_history = [x]
    warning_message = None

    for step_index in range(iteration_count):
        grad = df(x)
        x_new = x - learning_rate * grad
        if abs(x_new) > 1e6:
            warning_message = (
                f"Abbruch bei Schritt {step_index}: Gradient explodiert (x={x_new:.2e})"
            )
            break
        x = x_new
        x_history.append(x)

    curve_x = np.linspace(min(-10, min(x_history) - 1), max(10, max(x_history) + 1), 400)
    curve_df = pd.DataFrame({"x": curve_x, "y": f(curve_x)})
    history_df = pd.DataFrame(
        {
            "step": list(range(len(x_history))),
            "x": x_history,
            "y": [f(current_x) for current_x in x_history],
            "gradient": [df(current_x) for current_x in x_history],
        }
    )
    return {
        "curve_df": curve_df,
        "history_df": history_df,
        "warning": warning_message,
    }


if "gradient_config" not in st.session_state:
    st.session_state.gradient_config = DEFAULT_CONFIG.copy()
if "gradient_step" not in st.session_state:
    st.session_state.gradient_step = 0
if "gradient_is_animating" not in st.session_state:
    st.session_state.gradient_is_animating = False

st.sidebar.subheader("Einstellungen - Gradient Descent")
with st.sidebar.form("gradient_controls"):
    x0_input = st.slider(
        "Startwert x₀", -100.0, 100.0, float(st.session_state.gradient_config["x0"]), 0.5
    )
    lr_input = st.slider(
        "Lernrate η", 0.001, 0.5, float(st.session_state.gradient_config["lr"]), 0.001
    )
    iterations_input = st.slider(
        "Iterationen", 1, 30, int(st.session_state.gradient_config["iterations"])
    )
    save_config = st.form_submit_button("Verlauf berechnen", type="primary")

start_animation = st.sidebar.button("Animation starten")
stop_animation = st.sidebar.button("Animation stoppen")

if save_config:
    st.session_state.gradient_config = {
        "x0": float(x0_input),
        "lr": float(lr_input),
        "iterations": int(iterations_input),
    }
    st.session_state.gradient_is_animating = False

config = st.session_state.gradient_config
history_bundle = build_history(config["x0"], config["lr"], config["iterations"])
curve_df = history_bundle["curve_df"]
history_df = history_bundle["history_df"]
warning_message = history_bundle["warning"]
max_step = len(history_df) - 1

if save_config:
    st.session_state.gradient_step = max_step
st.session_state.gradient_step = min(st.session_state.gradient_step, max_step)

if start_animation:
    st.session_state.gradient_step = 0
    st.session_state.gradient_is_animating = True
if stop_animation:
    st.session_state.gradient_is_animating = False

st.sidebar.slider("Schritt", 0, max_step, key="gradient_step")
selected_step = st.session_state.gradient_step

if warning_message:
    st.warning(str(warning_message))


def build_chart(step: int) -> alt.Chart:
    visible_history = history_df.iloc[: step + 1]

    curve = (
        alt.Chart(curve_df)
        .mark_line(color="#2563eb", strokeWidth=3)
        .encode(
            x=alt.X("x:Q", title="x"),
            y=alt.Y("y:Q", title="f(x)"),
        )
    )

    trail = (
        alt.Chart(visible_history)
        .mark_circle(color="#ef4444", size=90)
        .encode(x="x:Q", y="y:Q", tooltip=["step", "x", "y", "gradient"])
    )

    current = (
        alt.Chart(visible_history.tail(1))
        .mark_circle(color="#22c55e", size=220)
        .encode(x="x:Q", y="y:Q", tooltip=["step", "x", "y", "gradient"])
    )

    return (curve + trail + current).properties(height=420)


st.altair_chart(build_chart(selected_step), width="stretch")

if st.session_state.gradient_is_animating:
    st.info(
        "Animation laeuft. Die Visualisierung bleibt sichtbar und wird Schritt fuer Schritt aktualisiert."
    )

current_row = history_df.iloc[selected_step]
final_row = history_df.iloc[-1]

formula_col, current_col, final_col = st.columns(3)
with formula_col:
    st.write("Wir betrachten die Funktion:")
    st.latex(r"f(x) = \frac{1}{2} x^2")
    st.write("und ihren Gradienten:")
    st.latex(r"f'(x) = x")
with current_col:
    st.metric("Aktueller Schritt", int(current_row["step"]))
    st.metric("x", f"{current_row['x']:.4f}")
    st.metric("f(x)", f"{current_row['y']:.4f}")
with final_col:
    st.metric("Finales x", f"{final_row['x']:.4f}")
    st.metric("Finales f(x)", f"{final_row['y']:.4f}")
    st.metric("Finaler Gradient", f"{final_row['gradient']:.4f}")

st.subheader("Erklärung")
st.markdown(r"""
Diese App visualisiert das **Gradient Descent** Verfahren zur Optimierung einer Funktion.

- Wähle im **Sidebar** den Startwert $x_0$, die Lernrate $\eta$ und die Anzahl der Iterationen.
- Klicke auf **Verlauf berechnen**, um neue Parameter zu übernehmen.
- Starte danach die Animation oder bewege den Slider **Schritt** manuell.
""")

with st.expander("Verlauf der Schritte"):
    st.dataframe(history_df.round(4), width="stretch", hide_index=True)

with st.expander("Erklärung zum Gradient Descent"):
    st.write("""
Gradient Descent (deutsch: Gradientenabstieg) ist ein Optimierungsverfahren, das häufig in der Mathematik, Statistik und im Machine Learning verwendet wird, um das Minimum einer Funktion zu finden.

**Grundidee:**
- Man startet an einem Punkt $$x_0$ auf der Kurve der Funktion $f(x)$.
- Berechnet den Gradienten $f'(x)$, der die Steigung der Funktion an diesem Punkt angibt.
- Geht in die entgegengesetzte Richtung des Gradienten (weil wir das Minimum suchen) mit einer Schrittweite, die durch die **Lernrate** $\\eta$ bestimmt wird:\n
$x_{\text{neu}} = x - \\eta \\cdot f'(x)$

**Parameter:**
1. **Startwert $x_0$**: Ausgangspunkt für den Algorithmus.
2. **Lernrate $\\eta$**: Bestimmt die Größe der Schritte. Zu große Werte können den Algorithmus instabil machen, zu kleine Werte verlangsamen die Konvergenz.
3. **Iterationen**: Anzahl der Schritte, die durchgeführt werden.

**Visualisierung:**
- Die **blaue Linie** zeigt die Funktion $f(x)$.
- Die **roten Punkte** zeigen die bisherigen Schritte des Gradient Descent.
- Der **grüne Punkt** zeigt den aktuellen Punkt, an dem wir uns befinden.

**Ziel:**
- Der Algorithmus nähert sich Schritt für Schritt dem Minimum der Funktion.
- Bei $f(x) = 0.5 x^2$ ist das Minimum bei $x = 0$.
""")

if st.session_state.gradient_is_animating:
    if st.session_state.gradient_step < max_step:
        time.sleep(0.14)
        st.session_state.gradient_step += 1
        st.rerun()
    else:
        st.session_state.gradient_is_animating = False
