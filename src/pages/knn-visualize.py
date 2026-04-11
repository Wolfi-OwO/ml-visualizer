import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

DEFAULT_KNN_SETTINGS = {
    "k": 3,
    "animate": False,
}

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
        reset_points()
    if "knn_animation_queue" not in st.session_state:
        st.session_state.knn_animation_queue = []
    if "knn_animation_neighbor_count" not in st.session_state:
        st.session_state.knn_animation_neighbor_count = 0
    if "knn_animation_k" not in st.session_state:
        st.session_state.knn_animation_k = DEFAULT_KNN_SETTINGS["k"]
    if "knn_settings" not in st.session_state:
        st.session_state.knn_settings = DEFAULT_KNN_SETTINGS.copy()
    if "knn_last_results" not in st.session_state:
        st.session_state.knn_last_results = []


def reset_points() -> None:
    points, unclassified = seeded_points()
    st.session_state.knn_points = points
    st.session_state.knn_unclassified_points = unclassified
    st.session_state.knn_animation_running = False
    st.session_state.knn_animation_queue = []
    st.session_state.knn_animation_neighbor_count = 0
    st.session_state.knn_last_results = []


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


def resolve_point(
    x_value: float, y_value: float, k_neighbors: int
) -> tuple[str, list[tuple[float, float, str]]]:
    distances = [
        (np.hypot(px - x_value, py - y_value), label, px, py)
        for px, py, label in st.session_state.knn_points
    ]
    distances.sort(key=lambda item: item[0])
    nearest_neighbors = [(px, py, label) for _, label, px, py in distances[:k_neighbors]]
    nearest_labels = [label for _, _, label in nearest_neighbors]
    unique_labels, counts = np.unique(nearest_labels, return_counts=True)
    predicted_label = str(unique_labels[counts.argmax()])
    return predicted_label, nearest_neighbors


def classify_points(k_neighbors: int) -> list[tuple[float, float, str]]:
    pending_points = list(st.session_state.knn_unclassified_points)
    resolved_points: list[tuple[float, float, str]] = []

    for x_value, y_value in pending_points:
        predicted_label, _ = resolve_point(x_value, y_value, k_neighbors)
        st.session_state.knn_points.append((x_value, y_value, predicted_label))
        resolved_points.append((x_value, y_value, predicted_label))

    st.session_state.knn_unclassified_points = []
    st.session_state.knn_last_results = resolved_points
    return resolved_points


def start_animation(k_neighbors: int) -> None:
    st.session_state.knn_animation_running = True
    st.session_state.knn_animation_k = k_neighbors
    st.session_state.knn_animation_queue = list(st.session_state.knn_unclassified_points)
    st.session_state.knn_unclassified_points = []
    st.session_state.knn_animation_neighbor_count = 1
    st.session_state.knn_last_results = []


ensure_state()

st.sidebar.subheader("Einstellungen - KNN")
with st.sidebar.form("knn_controls"):
    k = st.slider("Anzahl der Nachbarn k", 1, 15, int(st.session_state.knn_settings["k"]))
    animate = st.checkbox(
        "Klassifikation animieren",
        value=bool(st.session_state.knn_settings["animate"]),
    )
    classify_button = st.form_submit_button("Klassifikation starten", type="primary")
reset_button = st.sidebar.button("Alle Punkte zuruecksetzen")
stop_animation = st.sidebar.button("Animation stoppen")

if reset_button:
    reset_points()

if stop_animation and st.session_state.knn_animation_running:
    st.session_state.knn_unclassified_points = list(st.session_state.knn_animation_queue)
    st.session_state.knn_animation_running = False
    st.session_state.knn_animation_queue = []
    st.session_state.knn_animation_neighbor_count = 0

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
    st.session_state.knn_settings = {
        "k": int(k),
        "animate": bool(animate),
    }
    if not st.session_state.knn_unclassified_points:
        st.info("Keine neuen Punkte zum Klassifizieren vorhanden.")
    elif len(st.session_state.knn_points) < k:
        st.warning(
            "Nicht genug klassifizierte Punkte fuer KNN "
            f"(benoetigt: {k}, vorhanden: {len(st.session_state.knn_points)})."
        )
    elif animate:
        start_animation(k)
    else:
        resolved_points = classify_points(k)
        for x_value, y_value, label in resolved_points:
            st.success(f"Punkt ({x_value:.2f}, {y_value:.2f}) -> Klasse {label}")

if st.session_state.knn_animation_running and st.session_state.knn_animation_queue:
    current_point = st.session_state.knn_animation_queue[0]
    _, nearest_neighbors = resolve_point(
        current_point[0], current_point[1], st.session_state.knn_animation_k
    )
    visible_neighbors = nearest_neighbors[: st.session_state.knn_animation_neighbor_count]
    chart_placeholder.altair_chart(
        build_knn_chart(
            st.session_state.knn_points,
            list(st.session_state.knn_animation_queue[1:]),
            neighbors=visible_neighbors,
            highlight_point=(current_point[0], current_point[1], "?"),
        ),
        width="stretch",
    )
else:
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
    st.metric(
        "Offene Punkte",
        len(st.session_state.knn_unclassified_points) + len(st.session_state.knn_animation_queue),
    )

st.markdown(
    "**Legende:** Blau = Klasse A, Orange = Klasse B, Grau = offen, Gelb = aktuelle Nachbarn"
)
if st.session_state.knn_animation_running:
    st.info(
        "Animation laeuft. Die Nachbarn werden ohne kompletten Seiten-Block Schritt fuer Schritt angezeigt."
    )
elif st.session_state.knn_unclassified_points:
    st.info(f"{len(st.session_state.knn_unclassified_points)} Punkt(e) warten auf Klassifikation.")

if st.session_state.knn_last_results:
    st.subheader("Letzte Klassifikationen")
    st.table(
        pd.DataFrame(
            [
                {"x": round(x_value, 3), "y": round(y_value, 3), "Klasse": label}
                for x_value, y_value, label in st.session_state.knn_last_results
            ]
        )
    )

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

if st.session_state.knn_animation_running and st.session_state.knn_animation_queue:
    current_point = st.session_state.knn_animation_queue[0]
    predicted_label, nearest_neighbors = resolve_point(
        current_point[0],
        current_point[1],
        st.session_state.knn_animation_k,
    )
    max_neighbors = min(st.session_state.knn_animation_k, len(nearest_neighbors))

    if st.session_state.knn_animation_neighbor_count < max_neighbors:
        time.sleep(0.14)
        st.session_state.knn_animation_neighbor_count += 1
        st.rerun()
    else:
        st.session_state.knn_points.append((current_point[0], current_point[1], predicted_label))
        st.session_state.knn_last_results.append(
            (current_point[0], current_point[1], predicted_label)
        )
        st.session_state.knn_animation_queue = st.session_state.knn_animation_queue[1:]
        if st.session_state.knn_animation_queue:
            st.session_state.knn_animation_neighbor_count = 1
            time.sleep(0.12)
            st.rerun()
        else:
            st.session_state.knn_animation_running = False
            st.session_state.knn_animation_neighbor_count = 0
