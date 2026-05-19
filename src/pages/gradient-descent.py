import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

DEFAULT_CONFIG = {
    "x0": 8.0,
    "lr": 0.1,
    "iterations": 20,
}

st.title("Gradient Descent Visualizer")


# FUNKTION
def f(x):
    return 0.5 * x**2


def df(x):
    return x


@st.cache_data(show_spinner=False)
def build_history(start_x, lr, iterations):
    x = float(start_x)
    xs = [x]

    for _ in range(iterations):
        x = x - lr * df(x)
        xs.append(x)

    x_min = min(xs)
    x_max = max(xs)
    margin = max(abs(x_max - x_min) * 0.2, 1.0)

    curve_x = np.linspace(x_min - margin, x_max + margin, 400)
    curve_df = pd.DataFrame({"x": curve_x, "y": f(curve_x)})

    history_df = pd.DataFrame(
        {
            "step": range(len(xs)),
            "x": xs,
            "y": [f(v) for v in xs],
            "gradient": [df(v) for v in xs],
        }
    )

    return curve_df, history_df


# STATE initialisieren
if "config" not in st.session_state:
    st.session_state.config = DEFAULT_CONFIG.copy()

if "step" not in st.session_state:
    st.session_state.step = 0

if "animating" not in st.session_state:
    st.session_state.animating = False


# SIDEBAR — Einstellungen (KEIN Form, damit Änderungen sofort wirken)
st.sidebar.subheader("Einstellungen")

x0 = st.sidebar.slider(
    "Startwert x₀",
    -15.0,
    15.0,
    st.session_state.config["x0"],
    0.5,
    key="slider_x0",
)
lr = st.sidebar.slider(
    "Lernrate η",
    0.01,
    0.95,
    st.session_state.config["lr"],
    0.01,
    key="slider_lr",
)
iters = st.sidebar.slider(
    "Iterationen",
    1,
    50,
    st.session_state.config["iterations"],
    1,
    key="slider_iters",
)

# Erkennen ob Parameter geändert wurden → State zurücksetzen
new_config = {"x0": x0, "lr": lr, "iterations": iters}
if new_config != st.session_state.config:
    st.session_state.config = new_config
    st.session_state.step = 0
    st.session_state.animating = False

# DATEN berechnen (mit aktuellen Parametern)
curve_df, history_df = build_history(
    st.session_state.config["x0"],
    st.session_state.config["lr"],
    st.session_state.config["iterations"],
)

max_step = len(history_df) - 1

# Schritt innerhalb Grenzen halten
st.session_state.step = min(st.session_state.step, max_step)

# ANIMATIONSSTEUERUNG
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("▶ Start", use_container_width=True):
        st.session_state.animating = True
        if st.session_state.step >= max_step:
            st.session_state.step = 0
with col2:
    if st.button("■ Stop", use_container_width=True):
        st.session_state.animating = False

# SCHRITT-SLIDER (manuell)
# Nur anzeigen wenn nicht animiert, damit kein Konflikt entsteht
if not st.session_state.animating:
    manual_step = st.sidebar.slider(
        "Schritt",
        0,
        max_step,
        st.session_state.step,
        key="manual_step_slider",
    )
    st.session_state.step = manual_step
else:
    st.sidebar.write(f"Schritt: {st.session_state.step} / {max_step}")

step = st.session_state.step


# CHART
def make_chart(step):
    vis = history_df.iloc[: step + 1].copy()

    base = (
        alt.Chart(curve_df)
        .mark_line(color="#888", strokeWidth=2)
        .encode(x=alt.X("x", title="x"), y=alt.Y("y", title="f(x)"))
    )

    trail = (
        alt.Chart(vis)
        .mark_circle(size=80, color="#1D9E75", opacity=0.8)
        .encode(
            x="x",
            y="y",
            tooltip=[
                alt.Tooltip("step", title="Schritt"),
                alt.Tooltip("x", format=".4f"),
                alt.Tooltip("y", title="f(x)", format=".4f"),
                alt.Tooltip("gradient", title="f'(x)", format=".4f"),
            ],
        )
    )

    current_pt = vis.tail(1)
    current = alt.Chart(current_pt).mark_circle(size=250, color="#D85A30").encode(x="x", y="y")

    return (base + trail + current).properties(height=420).interactive()


st.altair_chart(make_chart(step), use_container_width=True)

# INFO
current = history_df.iloc[step]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Schritt", f"{step} / {max_step}")
c2.metric("x", f"{current['x']:.4f}")
c3.metric("f(x)", f"{current['y']:.4f}")
c4.metric("f'(x)", f"{current['gradient']:.4f}")


# ANIMATIONSLOGIK — nach dem Chart ausführen
if st.session_state.animating:
    if st.session_state.step < max_step:
        time.sleep(0.25)
        st.session_state.step += 1
        st.rerun()
    else:
        st.session_state.animating = False


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
