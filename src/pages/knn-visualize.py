import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="K-Nearest-Neighbors Algorithm", layout="wide")

st.title("KNN (K-Nearest Neighbors) Visualizer")
st.caption("Fuege Punkte hinzu und klassifiziere alle offenen Punkte mit einem Klick.")


def seeded_points() -> tuple[list[tuple[float, float, str]], list[tuple[float, float]]]:
    rng = np.random.default_rng(42)
    class_a = rng.multivariate_normal([0.3, 0.3], [[0.01, 0], [0, 0.01]], 5)
    class_b = rng.multivariate_normal([0.7, 0.7], [[0.01, 0], [0, 0.01]], 5)
    points = [(float(x), float(y), "A") for x, y in class_a]
    points += [(float(x), float(y), "B") for x, y in class_b]
    return points, []


def ensure_state() -> None:
    if "knn_points" not in st.session_state:
        points, unclassified = seeded_points()
        st.session_state.knn_points = points
        st.session_state.knn_unclassified_points = unclassified
        st.session_state.knn_animation_running = False


def build_knn_chart(
    points: list[tuple[float, float, str]],
    unclassified_points: list[tuple[float, float]],
    neighbors: list[tuple[float, float, str]] | None = None,
    highlight_point: tuple[float, float, str] | None = None,
) -> alt.Chart:
    rows: list[dict[str, object]] = []

    for x_value, y_value, label in points:
        rows.append(
            {
                "x": x_value,
                "y": y_value,
                "label": label,
                "color": "#2563eb" if label == "A" else "#f97316",
                "shape": "circle",
                "size": 140,
                "tooltip": f"Klasse {label}",
            }
        )

    for x_value, y_value in unclassified_points:
        rows.append(
            {
                "x": x_value,
                "y": y_value,
                "label": "?",
                "color": "#6b7280",
                "shape": "triangle-up",
                "size": 180,
                "tooltip": "Unklassifiziert",
            }
        )

    for x_value, y_value, label in neighbors or []:
        rows.append(
            {
                "x": x_value,
                "y": y_value,
                "label": label,
                "color": "#facc15",
                "shape": "diamond",
                "size": 230,
                "tooltip": f"Nachbar {label}",
            }
        )

    if highlight_point is not None:
        rows.append(
            {
                "x": highlight_point[0],
                "y": highlight_point[1],
                "label": highlight_point[2],
                "color": "#111827",
                "shape": "triangle-up",
                "size": 260,
                "tooltip": "Aktueller Punkt",
            }
        )

    plot_df = pd.DataFrame(rows)
    if plot_df.empty:
        plot_df = pd.DataFrame(
            [
                {
                    "x": 0.0,
                    "y": 0.0,
                    "label": "",
                    "color": "#000000",
                    "shape": "circle",
                    "size": 0,
                    "tooltip": "",
                }
            ]
        ).iloc[0:0]

    return (
        alt.Chart(plot_df)
        .mark_point(filled=True)
        .encode(
            x=alt.X("x:Q", scale=alt.Scale(domain=[0, 1]), title="x"),
            y=alt.Y("y:Q", scale=alt.Scale(domain=[0, 1]), title="y"),
            color=alt.Color("color:N", scale=None, legend=None),
            shape=alt.Shape("shape:N", scale=None, legend=None),
            size=alt.Size("size:Q", scale=None, legend=None),
            tooltip=["tooltip:N", "x:Q", "y:Q"],
        )
        .properties(height=420)
    )


def classify_points(
    k_neighbors: int, animate_steps: bool, chart_placeholder
) -> list[tuple[float, float, str]]:
    pending_points = list(st.session_state.knn_unclassified_points)
    resolved_points: list[tuple[float, float, str]] = []
    st.session_state.knn_animation_running = True

    for x_value, y_value in pending_points:
        distances = [
            (np.hypot(px - x_value, py - y_value), label, px, py)
            for px, py, label in st.session_state.knn_points
        ]
        distances.sort(key=lambda item: item[0])

        if animate_steps:
            for neighbor_count in range(1, k_neighbors + 1):
                current_neighbors = [
                    (px, py, label) for _, label, px, py in distances[:neighbor_count]
                ]
                chart_placeholder.altair_chart(
                    build_knn_chart(
                        st.session_state.knn_points,
                        [],
                        neighbors=current_neighbors,
                        highlight_point=(x_value, y_value, "?"),
                    ),
                    width="stretch",
                )
                time.sleep(0.2)

        nearest_labels = [label for _, label, _, _ in distances[:k_neighbors]]
        unique_labels, counts = np.unique(nearest_labels, return_counts=True)
        predicted_label = str(unique_labels[counts.argmax()])

        st.session_state.knn_points.append((x_value, y_value, predicted_label))
        resolved_points.append((x_value, y_value, predicted_label))

    st.session_state.knn_unclassified_points = []
    st.session_state.knn_animation_running = False
    return resolved_points


ensure_state()

st.sidebar.subheader("Einstellungen - KNN")
k = st.sidebar.slider("Anzahl der Nachbarn k", 1, 15, 3)
animate = st.sidebar.checkbox("Klassifikation animieren", value=False)
classify_button = st.sidebar.button("Klassifikation starten", type="primary")
reset_button = st.sidebar.button("Alle Punkte zuruecksetzen")

if reset_button:
    points, unclassified = seeded_points()
    st.session_state.knn_points = points
    st.session_state.knn_unclassified_points = unclassified
    st.session_state.knn_animation_running = False

left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    st.subheader("Punkt hinzufuegen")
    with st.form("add_point_form"):
        x_input = st.number_input(
            "X-Koordinate", min_value=0.0, max_value=1.0, value=0.5, step=0.01
        )
        y_input = st.number_input(
            "Y-Koordinate", min_value=0.0, max_value=1.0, value=0.5, step=0.01
        )
        class_input = st.selectbox("Klasse", options=["Unclassified", "A", "B"], index=0)
        add_point_button = st.form_submit_button("Punkt hinzufuegen")

with right_col:
    chart_placeholder = st.empty()

if add_point_button and not st.session_state.knn_animation_running:
    x_value = float(x_input)
    y_value = float(y_input)
    point_exists = any(
        abs(px - x_value) < 0.01 and abs(py - y_value) < 0.01
        for px, py, _ in st.session_state.knn_points
    )
    unclassified_exists = any(
        abs(px - x_value) < 0.01 and abs(py - y_value) < 0.01
        for px, py in st.session_state.knn_unclassified_points
    )

    if point_exists or unclassified_exists:
        st.warning("Dieser Punkt existiert bereits.")
    elif class_input == "Unclassified":
        st.session_state.knn_unclassified_points.append((x_value, y_value))
        st.info(f"Punkt ({x_value:.2f}, {y_value:.2f}) wartet auf Klassifikation.")
    else:
        st.session_state.knn_points.append((x_value, y_value, class_input))
        st.success(
            f"Punkt ({x_value:.2f}, {y_value:.2f}) wurde als Klasse {class_input} gespeichert."
        )

if classify_button:
    if not st.session_state.knn_unclassified_points:
        st.info("Keine neuen Punkte zum Klassifizieren vorhanden.")
    elif len(st.session_state.knn_points) < k:
        st.warning(
            "Nicht genug klassifizierte Punkte fuer KNN "
            f"(benoetigt: {k}, vorhanden: {len(st.session_state.knn_points)})."
        )
    else:
        resolved_points = classify_points(k, animate, chart_placeholder)
        for x_value, y_value, label in resolved_points:
            st.success(f"Punkt ({x_value:.2f}, {y_value:.2f}) -> Klasse {label}")

chart_placeholder.altair_chart(
    build_knn_chart(st.session_state.knn_points, st.session_state.knn_unclassified_points),
    width="stretch",
)

metric_col1, metric_col2, metric_col3 = st.columns(3)
with metric_col1:
    st.metric("Klasse A", sum(label == "A" for _, _, label in st.session_state.knn_points))
with metric_col2:
    st.metric("Klasse B", sum(label == "B" for _, _, label in st.session_state.knn_points))
with metric_col3:
    st.metric("Offene Punkte", len(st.session_state.knn_unclassified_points))

st.markdown(
    "**Legende:** Blau = Klasse A, Orange = Klasse B, Grau = offen, Gelb = aktuelle Nachbarn"
)
if st.session_state.knn_unclassified_points:
    st.info(f"{len(st.session_state.knn_unclassified_points)} Punkt(e) warten auf Klassifikation.")

st.subheader("Anleitung")
st.markdown(
    """
    1. Gib X- und Y-Koordinaten ein und waehle die Klasse oder **Unclassified**.
    2. Fuege den Punkt hinzu.
    3. Starte die Klassifikation ueber die Sidebar.
    4. Mit aktivierter Animation siehst du die ausgewaehlten Nachbarn Schritt fuer Schritt.
    """
)

with st.expander("Erklaerung zum KNN"):
    st.markdown(
        """
**K-Nearest Neighbors (KNN)** klassifiziert neue Punkte ueber ihre naechsten Nachbarn.

1. Distanzen zu allen bekannten Punkten berechnen
2. Die **k** kleinsten Distanzen auswaehlen
3. Die haeufigste Klasse dieser Nachbarn uebernehmen

Der Algorithmus braucht kein separates Training. Er nutzt direkt die vorhandenen Datenpunkte.
        """
    )
