import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Gradient Descent - Optimierungsverfahren", layout="wide")

st.title("Gradient Descent Visualizer")

col1, col2 = st.columns([1, 2])

with col1:
    st.write("Wir betrachten die Funktion:")
    st.latex(r"f(x) = \frac{1}{2} x^2")

    st.write("und ihren Gradienten:")
    st.latex(r"f'(x) = x")


# Funktion und Ableitung
def f(x):
    return 0.5 * x**2


def df(x):
    return x


# Sidebar-Parameter
st.sidebar.subheader("Einstellungen - Gradient Descent")
x0 = st.sidebar.slider("Startwert x₀", -100.0, 100.0, 8.0, 0.5)
lr = st.sidebar.slider("Lernrate η", 0.001, 0.5, 0.005, 0.001)
iterations = st.sidebar.slider("Iterationen", 1, 30, 15)
animate = st.sidebar.button("Animation starten")

# Berechnung
x = x0
x_history = [x]
for i in range(iterations):
    grad = df(x)
    x_new = x - lr * grad
    if abs(x_new) > 1e6:
        st.warning(f"Abbruch bei Schritt {i}: Gradient explodiert (x={x_new:.2e})")
        break
    x = x_new
    x_history.append(x)

placeholder = st.empty()
x_min = min(-10, min(x_history) - 1)
x_max = max(10, max(x_history) + 1)
x_vals = np.linspace(x_min, x_max, 400)
y_vals = f(x_vals)
df_func = pd.DataFrame({"x": x_vals, "y": y_vals})

with col2:

    def plot_altair(step):
        # Verlauf der Gradientenpunkte
        df_points = pd.DataFrame(
            {
                "x": x_history[: step + 1],
                "y": [f(x) for x in x_history[: step + 1]],
                "step": list(range(step + 1)),
            }
        )

        # Linie der Funktion
        base = alt.Chart(df_func).mark_line(color="blue").encode(x="x", y="y")

        # Schritte als rote Punkte
        points = alt.Chart(df_points).mark_circle(color="red", size=100).encode(x="x", y="y")

        # Aktueller Punkt als grüner Punkt
        current = (
            alt.Chart(df_points.iloc[[-1]]).mark_circle(color="lime", size=200).encode(x="x", y="y")
        )

        chart = base + points + current
        st.altair_chart(chart, width="stretch")

    if animate:
        placeholder = st.empty()  # Placeholder für die Animation
        for step in range(len(x_history)):
            with placeholder.container():  # Überschreibt den vorherigen Chart
                plot_altair(step)
            time.sleep(0.25)
    else:
        step = st.slider("Manueller Schritt", 0, len(x_history) - 1, 0)
        plot_altair(step)


st.success(f"Aktueller Punkt: x ≈ {x_history[-1]:.4f}, f(x) = {f(x_history[-1]):.4f}")

st.subheader("Erklärung")
st.markdown(r"""
Diese App visualisiert das **Gradient Descent** Verfahren zur Optimierung einer Funktion.

- Wähle im **Sidebar** den Startwert $x_0$, die Lernrate $\eta$ und die Anzahl der Iterationen.
- Klicke auf **Animation starten**, um den Schritt-für-Schritt-Verlauf automatisch zu sehen.
- Alternativ kannst du den Fortschritt manuell mit dem Slider "Manueller Schritt" verfolgen.
""")


# --------------------------------------------------
# Explanation
# --------------------------------------------------
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

Durch das Anpassen der Parameter kannst du beobachten, wie sich Startwert und Lernrate auf die Geschwindigkeit und Stabilität des Verfahrens auswirken.
""")
