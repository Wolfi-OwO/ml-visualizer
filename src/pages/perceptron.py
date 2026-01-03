import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Perceptron Visualizer",
    layout="wide",
)

st.title("Perceptron - Interaktive Lernvisualisierung")

st.markdown(
    """
    Ein **Perceptron** ist das einfachste neuronale Netzwerk.
    Es lernt eine **lineare Entscheidungsgrenze**.
    """
)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
st.sidebar.header("Einstellungen")

lr = st.sidebar.slider("Lernrate η", 0.01, 1.0, 0.3, 0.01)
epochs = st.sidebar.slider("Epochen", 1, 20, 5)
start = st.sidebar.button("▶ Training starten")

# --------------------------------------------------
# Data (AND)
# --------------------------------------------------
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([0, 0, 0, 1])

# --------------------------------------------------
# Training
# --------------------------------------------------
np.random.seed(42)
w = np.random.uniform(-1, 1, 2)
b = np.random.uniform(-1, 1)

history = [(w.copy(), b)]

for _ in range(epochs):
    for i in range(len(X)):
        z = np.dot(X[i], w) + b
        y_hat = 1 if z > 0 else 0
        error = y[i] - y_hat
        w += lr * error * X[i]
        b += lr * error
        history.append((w.copy(), b))


# --------------------------------------------------
# Plot function
# --------------------------------------------------
def plot_decision_boundary(weights, bias):
    x_vals = np.linspace(-0.2, 1.2, 100)
    y_vals = -(weights[0] * x_vals + bias) / weights[1]

    df_line = pd.DataFrame({"x": x_vals, "y": y_vals})

    df_points = pd.DataFrame(X, columns=["x", "y"])
    df_points["class"] = y.astype(str)

    points = (
        alt.Chart(df_points)
        .mark_circle(size=200)
        .encode(
            x="x", y="y", color=alt.Color("class:N", scale=alt.Scale(range=["#ff7f0e", "#1f77b4"]))
        )
    )

    line = alt.Chart(df_line).mark_line(color="black").encode(x="x", y="y")

    return (points + line).properties(width=600, height=400)


# --------------------------------------------------
# Layout
# --------------------------------------------------
left, right = st.columns([1, 2])

with right:
    plot_placeholder = st.empty()

with left:
    state_box = st.empty()

# --------------------------------------------------
# Visualization
# --------------------------------------------------
if start:
    for step, (w, b) in enumerate(history):
        plot_placeholder.altair_chart(
            plot_decision_boundary(w, b),
            width="stretch",
        )
        state_box.info(f"Schritt {step}\n\nw₁={w[0]:.2f}\nw₂={w[1]:.2f}\nBias={b:.2f}")
        time.sleep(0.4)
else:
    plot_placeholder.altair_chart(
        plot_decision_boundary(w, b),
        width="stretch",
    )

st.subheader("Anleitung")
st.markdown(
    """
    1. **Lernrate (η) einstellen**
    Die Lernrate bestimmt, **wie stark** das Perceptron seine Gewichte bei einem Fehler anpasst.
    - Kleine Lernrate → langsames, aber stabiles Lernen
    - Große Lernrate → schnelles, aber eventuell instabiles Lernen

    2. **Anzahl der Epochen wählen**
    Eine Epoche bedeutet, dass **alle Trainingsdaten einmal durchlaufen werden**.
    Mehr Epochen = mehr Lernschritte.

    3. **„Training starten“ klicken**
    Nach dem Klick beginnt das Perceptron zu lernen.
    Du siehst Schritt für Schritt:
    - wie sich die **Entscheidungsgrenze (Linie)** verschiebt
    - wie sich die **Gewichte (w₁, w₂)** und der **Bias** verändern

    4. **Visualisierung verstehen**
    - 🔵 Punkte → Klasse **1**
    - 🟠 Punkte → Klasse **0**
    - ⚫ Linie → aktuelle Entscheidungsgrenze des Perceptrons

    Ziel des Trainings ist es, die Linie so zu verschieben,
    dass **nur der Punkt (1,1)** als **1** klassifiziert wird
    (AND-Operator).

    **Tipp:**
    Probiere verschiedene Lernraten und Epochen aus,
    um zu sehen, wie sich das Lernverhalten verändert.

    """
)

# --------------------------------------------------
# Explanation
# --------------------------------------------------
with st.expander("Erklärung zum Perceptron"):
    # --------------------------------------------------
    # THEORY - WHAT IS A PERCEPTRON
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("## Was ist ein Perceptron?")

    st.markdown(
        """
        Ein **Perceptron** ist das **einfachste neuronale Netzwerk** und auch der kleinste Baustein von einem.
        Es besteht aus:

        - mehreren Eingaben (x₁, x₂, …)
        - zugehörigen Gewichten (w₁, w₂, …)
        - einem Bias (b)
        - einer Aktivierungsfunktion
        """
    )

    st.markdown("### Mathematisches Modell")

    st.latex(r"z = w_1 x_1 + w_2 x_2 + b")

    st.markdown(
        """
        Die Ausgabe erfolgt über eine **Schwellwertfunktion**:
        """
    )

    st.latex(
        r"""
        \hat{y} =
        \begin{cases}
        1 & \text{wenn } z > 0 \\
        0 & \text{sonst}
        \end{cases}
        """
    )

    # --------------------------------------------------
    # LEARNING
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("## Wie lernt ein Perceptron?")

    st.markdown(
        """
        Das Perceptron lernt **durch Fehlerkorrektur** - einen iterativen Prozess,
        bei dem Fehler schrittweise minimiert werden.

        ### Der Lernprozess im Detail:

        1. **Initialisierung** - Gewichte und Bias werden zufällig gesetzt
        2. **Vorhersage berechnen** - Für jeden Trainingspunkt wird z = w·x + b berechnet
        3. **Fehler bestimmen** - Differenz zwischen erwartetem und vorhergesagtem Wert
        4. **Gewichte anpassen** - Korrektur basierend auf dem Fehler
        5. **Wiederholen** - Bis alle Punkte korrekt klassifiziert sind (oder Epochen-Limit erreicht)
        """
    )

    st.markdown("### Fehlerberechnung")

    st.latex(r"error = y - \hat{y}")

    st.markdown(
        """
        **Mögliche Fehler:**
        - error = +1 → Punkt sollte 1 sein, war aber 0 ⇒ Gewichte erhöhen
        - error = -1 → Punkt sollte 0 sein, war aber 1 ⇒ Gewichte verringern
        - error = 0 → Korrekte Vorhersage ⇒ keine Änderung
        """
    )

    st.markdown("### Update-Regeln (Perceptron-Lernregel)")

    st.latex(r"w = w + \eta \cdot error \cdot x")
    st.latex(r"b = b + \eta \cdot error")

    st.markdown(
        """
        ### Die Rolle der Lernrate η

        - **η = 0.1** → Kleine Schritte, stabiles aber langsames Lernen
        - **η = 0.5** → Moderate Schritte, guter Kompromiss
        - **η = 1.0** → Große Schritte, schnell aber potenziell instabil

        **Beispiel:** Bei error = 1, x = 0.5, η = 0.3:
        - w_neu = w_alt + 0.3 × 1 × 0.5 = w_alt + 0.15
        """
    )

    # --------------------------------------------------
    # LIMITATIONS
    # --------------------------------------------------
    st.markdown("---")
    st.markdown("## Einschränkungen & Anwendungen")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ❌ Limitierungen")
        st.markdown(
            """
            **Linear trennbare Probleme:**
            - Kann nur Probleme lösen, die durch eine **gerade Linie** (2D) oder
              **Hyperebene** (n-D) trennbar sind

            **Beispiele nicht lösbarer Probleme:**
            - **XOR** (Exclusive OR)
            - Kreisförmige Klassengrenzen
            - Verschachtelte Cluster

            **Warum?**
            - Ein einzelnes Perceptron kann nur **eine** Entscheidungsgrenze erzeugen
            - Komplexere Probleme benötigen **mehrere Schichten** (Multi-Layer Networks)
            """
        )

    with col2:
        st.markdown("### ✅ Praktische Anwendungen")
        st.markdown(
            """
            **Wo Perceptrons gut funktionieren:**
            - **Binäre Klassifikation** (2 Klassen)
            - **Sentiment-Analyse** (positiv/negativ)
            - **Spam-Filter** (Spam/Ham)
            - **Medizinische Diagnose** (krank/gesund)

            **Historische Bedeutung:**
            - 1957 von Frank Rosenblatt entwickelt
            - Grundstein für moderne neuronale Netze
            - Einfach, aber fundamental wichtig

            **Modernes Relevanz:**
            - Baustein in tiefen Netzen
            - Verständnisgrundlage für Backpropagation
            """
        )
