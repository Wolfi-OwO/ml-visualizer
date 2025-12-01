import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

st.title("KNN (K-Nearest Neighbors) Visualizer")

st.markdown(
    """
    Visualisiere, wie der KNN (K-Nearest Neighbors) Algorithmus funktioniert.
    Wähle die Anzahl der Nachbarn (k) und klicke auf das Diagramm, um Punkte hinzuzufügen.
    """
)

# Sidebar
st.sidebar.subheader("Einstellungen - KNN")
k = st.sidebar.slider("Anzahl der Nachbarn k", 1, 15, 3)
animate = st.sidebar.checkbox("Klassifikation animieren", value=False)
classify_button = st.sidebar.button("Klassifikation starten", type="primary")

# Beispiel-Daten generieren
if "points" not in st.session_state:
    np.random.seed(42)
    class_A = np.random.multivariate_normal([0.3, 0.3], [[0.01, 0], [0, 0.01]], 5)
    class_B = np.random.multivariate_normal([0.7, 0.7], [[0.01, 0], [0, 0.01]], 5)
    st.session_state.points = [(x, y, "A") for x, y in class_A] + [(x, y, "B") for x, y in class_B]
    st.session_state.animation_running = False
    st.session_state.unclassified_points = []  # Liste für neue, noch nicht klassifizierte Punkte

points = st.session_state.points


def plot_altair_with_animation(highlight_point=None, neighbors=None):
    df_points = pd.DataFrame(points, columns=["x", "y", "class"])

    # Basis-Chart mit Punkten
    base = (
        alt.Chart(df_points)
        .mark_point(filled=True, size=100)
        .encode(
            x=alt.X("x", scale=alt.Scale(domain=[0, 1]), title="X"),
            y=alt.Y("y", scale=alt.Scale(domain=[0, 1]), title="Y"),
            color=alt.Color(
                "class:N",
                scale=alt.Scale(domain=["A", "B"], range=["#1f77b4", "#ff7f0e"]),
            ),
        )
    )

    layers = [base]

    # Neuer Punkt (Dreieck)
    if highlight_point is not None:
        df_new = pd.DataFrame([highlight_point], columns=["x", "y", "class"])
        new_point = (
            alt.Chart(df_new)
            .mark_point(shape="triangle-up", size=200, color="gray", filled=True)
            .encode(x="x", y="y")
        )
        layers.append(new_point)

    # K-nächste Nachbarn (gelbe Kreise)
    if neighbors is not None and len(neighbors) > 0:
        df_neighbors = pd.DataFrame(neighbors, columns=["x", "y", "class"])
        neighbor_layer = (
            alt.Chart(df_neighbors)
            .mark_circle(size=400, color="yellow", opacity=0.4)
            .encode(x="x", y="y")
        )
        layers.append(neighbor_layer)

    chart = alt.layer(*layers).properties(width=600, height=400)

    return chart


st.markdown("**Klicke auf das Diagramm, um einen neuen Punkt hinzuzufügen:**")

# Erstelle ein dichtes Grid für Klicks
grid_size = 30  # Weniger Grid-Punkte
grid_x = np.linspace(0, 1, grid_size)
grid_y = np.linspace(0, 1, grid_size)
grid_points = []
for gx in grid_x:
    for gy in grid_y:
        grid_points.append(
            {
                "x": gx,
                "y": gy,
                "type": "grid",
                "size": 50,
                "opacity": 0.02,
                "color": "#cccccc",
            }
        )

# Füge existierende klassifizierte Punkte hinzu
for px, py, cls in points:
    color = "#1f77b4" if cls == "A" else "#ff7f0e"
    grid_points.append({"x": px, "y": py, "type": cls, "size": 150, "opacity": 1, "color": color})

# Füge unklassifizierte Punkte hinzu (grau)
if "unclassified_points" not in st.session_state:
    st.session_state.unclassified_points = []

for px, py in st.session_state.unclassified_points:
    grid_points.append(
        {"x": px, "y": py, "type": "?", "size": 150, "opacity": 1, "color": "#888888"}
    )

df_all = pd.DataFrame(grid_points)

# Click Selection
click = alt.selection_point(fields=["x", "y"], on="click", empty=False)

# Ein einzelner Chart mit direkten Spalten für Styling
chart = (
    alt.Chart(df_all)
    .mark_point(filled=True)
    .encode(
        x=alt.X("x:Q", scale=alt.Scale(domain=[0, 1]), title="X"),
        y=alt.Y("y:Q", scale=alt.Scale(domain=[0, 1]), title="Y"),
        size=alt.Size("size:Q", legend=None),
        opacity=alt.Opacity("opacity:Q", legend=None),
        color=alt.Color("color:N", scale=None, legend=None),
    )
    .add_params(click)
    .properties(width=600, height=400)
)

# Event handling
event = st.altair_chart(chart, on_select="rerun", key="chart")

# Verarbeite Klick-Event - Füge nur unklassifizierte Punkte hinzu
if event and event.get("selection") and event["selection"].get("param_1"):
    click_data = event["selection"]["param_1"]

    if click_data and len(click_data) > 0 and not st.session_state.animation_running:
        click_point = click_data[0]

        if "x" in click_point and "y" in click_point:
            x = float(click_point["x"])
            y = float(click_point["y"])

            # Prüfe ob dieser Punkt schon existiert
            point_exists = any(abs(p[0] - x) < 0.01 and abs(p[1] - y) < 0.01 for p in points)
            unclass_exists = any(
                abs(ux - x) < 0.01 and abs(uy - y) < 0.01
                for ux, uy in st.session_state.unclassified_points
            )

            if not point_exists and not unclass_exists:
                # Füge als unklassifizierten Punkt hinzu
                st.session_state.unclassified_points.append((x, y))
                st.rerun()

# Klassifizierungs-Button wurde gedrückt
if classify_button and len(st.session_state.unclassified_points) > 0:
    if len(points) >= k:
        st.session_state.animation_running = True

        for ux, uy in st.session_state.unclassified_points:
            new_point_temp = (ux, uy, "?")
            existing_points = points.copy()

            distances = [
                (np.sqrt((px - ux) ** 2 + (py - uy) ** 2), cls, px, py)
                for px, py, cls in existing_points
            ]
            distances.sort(key=lambda d: d[0])

            if animate:
                placeholder = st.empty()
                for i in range(1, k + 1):
                    current_neighbors = [(px, py, cls) for _, cls, px, py in distances[:i]]
                    chart_anim = plot_altair_with_animation(
                        highlight_point=new_point_temp, neighbors=current_neighbors
                    )
                    placeholder.altair_chart(chart_anim, width="content")
                    time.sleep(0.5)

            nearest_classes = [cls for _, cls, _, _ in distances[:k]]
            predicted_class = max(set(nearest_classes), key=nearest_classes.count)
            new_point = (ux, uy, predicted_class)
            st.session_state.points.append(new_point)
            st.success(f"✓ Punkt ({ux:.3f}, {uy:.3f}) → Klasse **{predicted_class}**")

        # Lösche unklassifizierte Punkte
        st.session_state.unclassified_points = []
        st.session_state.animation_running = False
        st.rerun()
    else:
        st.warning(
            f"Nicht genug klassifizierte Punkte für KNN (benötigt: {k}, vorhanden: {len(points)})"
        )

elif classify_button:
    st.info("Keine neuen Punkte zum Klassifizieren vorhanden.")

# Legende manuell anzeigen
st.markdown("**Legende:** 🔵 Klasse A | 🟠 Klasse B | ⚫ Unklassifiziert")

# Zeige Anzahl unklassifizierter Punkte
if len(st.session_state.unclassified_points) > 0:
    st.info(f"📍 {len(st.session_state.unclassified_points)} Punkt(e) warten auf Klassifikation")

# Reset Button
if st.button("Alle Punkte zurücksetzen"):
    np.random.seed(42)
    class_A = np.random.multivariate_normal([0.3, 0.3], [[0.01, 0], [0, 0.01]], 5)
    class_B = np.random.multivariate_normal([0.7, 0.7], [[0.01, 0], [0, 0.01]], 5)
    st.session_state.points = [(x, y, "A") for x, y in class_A] + [(x, y, "B") for x, y in class_B]
    st.session_state.unclassified_points = []
    st.rerun()

st.markdown(
    """
    **Anleitung:**
    1. Klicke auf das Diagramm, um neue Punkte hinzuzufügen (sie erscheinen grau).
    2. Drücke **„Klassifikation starten"** in der Sidebar, um alle grauen Punkte zu klassifizieren.
    3. Aktiviere **„Klassifikation animieren"**, um die Nachbarsuche schrittweise zu sehen.
    """
)
