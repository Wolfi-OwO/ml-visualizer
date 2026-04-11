import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Gradient Descent - Optimierungsverfahren", layout="wide")

st.title("Gradient Descent Visualizer")
st.caption("Beobachte, wie sich der Startwert mit jedem Schritt in Richtung Minimum bewegt.")


def f(x):
    return 0.5 * x**2


def df(x):
    return x


st.sidebar.subheader("Einstellungen - Gradient Descent")
x0 = st.sidebar.slider("Startwert x₀", -100.0, 100.0, 8.0, 0.5)
lr = st.sidebar.slider("Lernrate η", 0.001, 0.5, 0.005, 0.001)
iterations = st.sidebar.slider("Iterationen", 1, 30, 15)
animate = st.sidebar.button("Animation starten")

x = x0
x_history = [x]
for step_index in range(iterations):
    grad = df(x)
    x_new = x - lr * grad
    if abs(x_new) > 1e6:
        st.warning(f"Abbruch bei Schritt {step_index}: Gradient explodiert (x={x_new:.2e})")
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

if "gradient_step" not in st.session_state:
    st.session_state.gradient_step = 0

selected_step_default = (
    len(x_history) - 1
    if animate
    else min(
        st.session_state.gradient_step,
        len(x_history) - 1,
    )
)
selected_step = st.sidebar.slider("Schritt", 0, len(x_history) - 1, selected_step_default)
st.session_state.gradient_step = selected_step


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


chart_placeholder = st.empty()
if animate:
    for step in range(len(x_history)):
        chart_placeholder.altair_chart(build_chart(step), width="stretch")
        time.sleep(0.18)
else:
    chart_placeholder.altair_chart(build_chart(selected_step), width="stretch")

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
- Klicke auf **Animation starten**, um den Schritt-für-Schritt-Verlauf automatisch zu sehen.
- Alternativ kannst du den Fortschritt mit dem Slider **Schritt** verfolgen.
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
