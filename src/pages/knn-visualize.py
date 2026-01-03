import time

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="K-Nearest-Neighbors Algorithm", layout="wide")

st.title("KNN (K-Nearest Neighbors) Visualizer")

st.markdown(
    """
    Visualisiere, wie der KNN (K-Nearest Neighbors) Algorithmus funktioniert.
    Füge Punkte über die Eingaben hinzu und klicke auf 'Klassifikation starten', um unklassifizierte Punkte zu klassifizieren.
    """
)

# Sidebar
st.sidebar.subheader("Einstellungen - KNN")
k = st.sidebar.slider("Anzahl der Nachbarn k", 1, 15, 3)
animate = st.sidebar.checkbox("Klassifikation animieren", value=False)
classify_button = st.sidebar.button("Klassifikation starten", type="primary")

col1, col2 = st.columns([1, 3])

# Initialize points
if "points" not in st.session_state:
    np.random.seed(42)
    class_A = np.random.multivariate_normal([0.3, 0.3], [[0.01, 0], [0, 0.01]], 5)
    class_B = np.random.multivariate_normal([0.7, 0.7], [[0.01, 0], [0, 0.01]], 5)
    st.session_state.points = [(x, y, "A") for x, y in class_A] + [(x, y, "B") for x, y in class_B]
    st.session_state.unclassified_points = []
    st.session_state.animation_running = False

with col2:
    # Single placeholder for all charts
    chart_placeholder = st.empty()

    # Function to plot points
    def plot_points(points, unclassified_points, neighbors=None, highlight_point=None):
        # Always define all columns
        columns = ["x", "y", "class", "marker"]

        # Points
        df_list = []

        if points:
            df_points = pd.DataFrame(points, columns=["x", "y", "class"])
            df_points["marker"] = "point"
            df_list.append(df_points)

        if unclassified_points:
            df_unclassified = pd.DataFrame(unclassified_points, columns=["x", "y"])
            df_unclassified["class"] = "?"
            df_unclassified["marker"] = "point"
            df_list.append(df_unclassified)

        if highlight_point:
            df_highlight = pd.DataFrame([highlight_point], columns=["x", "y", "class"])
            df_highlight["marker"] = "highlight"
            df_list.append(df_highlight)

        if neighbors:
            df_neighbors = pd.DataFrame(neighbors, columns=["x", "y", "class"])
            df_neighbors["marker"] = "neighbor"
            df_list.append(df_neighbors)

        # Only concat non-empty DataFrames
        if df_list:
            df_plot = pd.concat(df_list, ignore_index=True)
        else:
            df_plot = pd.DataFrame(columns=columns)

        # Precompute visual attributes
        df_plot["color_col"] = df_plot.apply(
            lambda row: (
                "yellow"
                if row["marker"] == "neighbor"
                else (
                    "#1f77b4"
                    if row["class"] == "A"
                    else (
                        "#ff7f0e"
                        if row["class"] == "B"
                        else "gray"
                        if row["marker"] == "highlight"
                        else "#888888"
                    )
                )
            ),
            axis=1,
        )
        df_plot["shape_col"] = df_plot.apply(
            lambda row: (
                "triangle-up" if row["class"] == "?" or row["marker"] == "highlight" else "circle"
            ),
            axis=1,
        )
        df_plot["size_col"] = df_plot.apply(
            lambda row: 200 if row["marker"] in ["neighbor", "highlight"] else 100, axis=1
        )
        df_plot["opacity_col"] = df_plot.apply(
            lambda row: 0.5 if row["marker"] == "neighbor" else 1.0, axis=1
        )

        chart = (
            alt.Chart(df_plot)
            .mark_point(filled=True)
            .encode(
                x=alt.X("x:Q", scale=alt.Scale(domain=[0, 1])),
                y=alt.Y("y:Q", scale=alt.Scale(domain=[0, 1])),
                color=alt.Color("color_col:N", scale=None),
                shape=alt.Shape("shape_col:N", scale=None),
                size=alt.Size("size_col:Q", scale=None),
                opacity=alt.Opacity("opacity_col:Q", scale=None),
            )
            .properties(width=600, height=400)
        )

        return chart

    # Show initial chart
    chart_placeholder.altair_chart(
        plot_points(st.session_state.points, st.session_state.unclassified_points),
        width="stretch",
    )

with col1:
    # Input for new points
    st.subheader("Punkt hinzufügen")
    x_input = st.number_input("X-Koordinate", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    y_input = st.number_input("Y-Koordinate", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
    class_input = st.selectbox("Klasse", options=["Unclassified", "A", "B"], index=0)
    add_point_button = st.button("Punkt hinzufügen")

if add_point_button and not st.session_state.animation_running:
    x, y = float(x_input), float(y_input)
    point_exists = any(
        abs(px - x) < 0.01 and abs(py - y) < 0.01 for px, py, _ in st.session_state.points
    )
    unclass_exists = any(
        abs(ux - x) < 0.01 and abs(uy - y) < 0.01 for ux, uy in st.session_state.unclassified_points
    )

    if point_exists or unclass_exists:
        st.warning("Dieser Punkt existiert bereits.")
    else:
        if class_input == "Unclassified":
            st.session_state.unclassified_points.append((x, y))
            st.info(f"Punkt ({x:.2f}, {y:.2f}) als **unklassifiziert** hinzugefügt.")
        else:
            st.session_state.points.append((x, y, class_input))
            st.success(f"Punkt ({x:.2f}, {y:.2f}) → Klasse **{class_input}**")
        chart_placeholder.altair_chart(
            plot_points(st.session_state.points, st.session_state.unclassified_points),
            width="stretch",
        )

    # KNN Classification
    if classify_button and len(st.session_state.unclassified_points) > 0:
        if len(st.session_state.points) >= k:
            st.session_state.animation_running = True

            for ux, uy in st.session_state.unclassified_points:
                new_point_temp = (ux, uy, "?")
                existing_points = st.session_state.points.copy()

                distances = [
                    (np.sqrt((px - ux) ** 2 + (py - uy) ** 2), cls, px, py)
                    for px, py, cls in existing_points
                ]
                distances.sort(key=lambda d: d[0])

                # Animate neighbors
                if animate:
                    for i in range(1, k + 1):
                        current_neighbors = [(px, py, cls) for _, cls, px, py in distances[:i]]
                        chart_placeholder.altair_chart(
                            plot_points(
                                st.session_state.points,
                                [],
                                neighbors=current_neighbors,
                                highlight_point=new_point_temp,
                            ),
                            width="stretch",
                        )
                        time.sleep(0.5)

                # Predict class
                nearest_classes = [cls for _, cls, _, _ in distances[:k]]
                predicted_class = max(set(nearest_classes), key=nearest_classes.count)
                st.session_state.points.append((ux, uy, predicted_class))
                st.success(f"Punkt ({ux:.3f}, {uy:.3f}) → Klasse **{predicted_class}**")

            st.session_state.unclassified_points = []
            st.session_state.animation_running = False
            chart_placeholder.altair_chart(
                plot_points(st.session_state.points, st.session_state.unclassified_points),
                width="stretch",
            )
        else:
            st.warning(
                f"Nicht genug klassifizierte Punkte für KNN (benötigt: {k}, vorhanden: {len(st.session_state.points)})"
            )
    elif classify_button:
        st.info("Keine neuen Punkte zum Klassifizieren vorhanden.")

# Legend & Status
st.markdown("**Legende:** 🔵 Klasse A | 🟠 Klasse B | ⚫ Unklassifiziert")
if len(st.session_state.unclassified_points) > 0:
    st.info(f"📍 {len(st.session_state.unclassified_points)} Punkt(e) warten auf Klassifikation")

# Reset
if st.button("Alle Punkte zurücksetzen"):
    np.random.seed(42)
    class_A = np.random.multivariate_normal([0.3, 0.3], [[0.01, 0], [0, 0.01]], 5)
    class_B = np.random.multivariate_normal([0.7, 0.7], [[0.01, 0], [0, 0.01]], 5)
    st.session_state.points = [(x, y, "A") for x, y in class_A] + [(x, y, "B") for x, y in class_B]
    st.session_state.unclassified_points = []
    chart_placeholder.altair_chart(
        plot_points(st.session_state.points, st.session_state.unclassified_points),
        width="stretch",
    )

st.subheader("Anleitung")
st.markdown(
    """
    1. Gib X- und Y-Koordinaten ein und wähle die Klasse oder 'Unclassified'.
    2. Drücke **„Punkt hinzufügen"**, um ihn zum Diagramm hinzuzufügen.
    3. Drücke **„Klassifikation starten"**, um alle grauen Punkte zu klassifizieren.
    4. Aktiviere **„Klassifikation animieren"**, um die Nachbarsuche schrittweise zu sehen.
    """
)

# --------------------------------------------------
# Explanation
# --------------------------------------------------
with st.expander("Erklärung zum KNN (K-Nearest Neighbors)"):
    st.markdown("---")
    st.markdown("## Was ist K-Nearest Neighbors?")
    st.markdown(
        """
        **K-Nearest Neighbors (KNN)** ist ein einfacher, aber leistungsstarker Algorithmus
        für **Klassifikation** und **Regression**.

        **Grundidee:**
        - "Zeig mir deine Nachbarn, und ich sage dir, wer du bist"
        - Neue Punkte werden basierend auf ihren nächsten Nachbarn klassifiziert
        - Kein explizites Training nötig - der Algorithmus merkt sich alle Datenpunkte
        """
    )

    st.markdown("### Die 3 Schritte des KNN")
    st.markdown(
        """
        Der KNN-Algorithmus besteht aus genau **3 Schritten**, die für jeden neuen Punkt wiederholt werden:

        1. **Distanz berechnen** - Zu allen bekannten Punkten
        2. **K-Nächste auswählen** - Die k-nächstgelegenen Nachbarn finden
        3. **Majority Vote** - Die häufigste Klasse unter den Nachbarn wird gewählt
        """
    )

    st.markdown("---")
    st.markdown("## Klassifizierungsprozess im Detail")
    # Distanz markdowns
    st.markdown("#### 1. Distanz berechnen")
    st.markdown("""Die Distanz kann mittels 3 gängiger Algebraischer-Ausdrücke berechnet werden:""")

    # Manhatten Distanz
    st.markdown("**1. Manhattan-Distanz (L1-Norm)**")
    st.markdown(
        """
        Die einfachste, aber auch ungenaueste Weise, um die Distanz zwischen zwei Punkten zu berechnen.
        Sie summiert die **absoluten Differenzen** jeder Koordinate.

        **Beispiel:** Von (0, 0) zu (3, 4) = |3-0| + |4-0| = 7
        """
    )
    st.latex(r"D_{manhatten}(x,y) = \sum_{i=1}^{n} |x_i - y_i|")
    st.markdown("In Python würde das wie folgt aussehen:")

    manhatten_distance_code = """
    import numpy as np

    def manhatten_distance(data_points, new_point):
        return np.sum(np.abs(data_points - new_point))"""

    st.code(manhatten_distance_code, "python", line_numbers=True)

    # Euklidische Distanz
    st.markdown("**2. Euklidische Distanz (L2-Norm)**")
    st.markdown(
        """
        Die **am häufigsten verwendete** Distanzmetrik. Sie berechnet die direkte,
        gerade Linie zwischen zwei Punkten - wie mit einem Lineal gemessen.

        **Beispiel:** Von (0, 0) zu (3, 4) = √(3² + 4²) = √25 = 5

        Diese Distanz entspricht dem **Satz des Pythagoras**.
        """
    )
    st.latex(r"D_{euclidean}(x,y) = \sqrt{\sum_{i=1}^{n} (x_i - y_i)^2}")
    st.markdown("In Python würde das wie folgt aussehen:")

    euclidean__distance_code = """
    import numpy as np

    def euclidean_distance(data_points, new_point):
        return np.sqrt(np.sum((data_points - new_point) ** 2))"""

    st.code(euclidean__distance_code, "python", line_numbers=True)

    # Minkowski-Distanz
    st.markdown("**3. Minkowski-Distanz (Verallgemeinerung)**")
    st.markdown(
        """
        Die **Verallgemeinerung** der Manhattan- und Euklidischen Distanz.
        Der Parameter **p** bestimmt die Art der Distanzberechnung:

        - **p = 1** → Manhattan-Distanz
        - **p = 2** → Euklidische Distanz
        - **p → ∞** → Maximum-Distanz (größte Koordinatendifferenz)
        """
    )
    st.latex(r"D_{minkowski}(x,y) = (\sum_{i=1}^{n} |x_i - y_i|^p) ^ {\frac{1}{p}}")
    st.markdown("In Python würde das wie folgt aussehen:")

    minkowski_distance_code = """
    import numpy as np

    def minkowski_distance(data_points, new_point, p):
        return (np.sum(np.abs(data_points - new_point) ** p) ** (1/p))"""

    st.code(minkowski_distance_code, "python", line_numbers=True)

    st.markdown("#### 2. K-Nearest herausholen ")
    st.markdown(
        "Nachdem alle Distanzen berechnet wurden, werden diese aufsteigend sortiert. Danach werden die k-nächsten heraus geholt, was in Python wie folgt realisiert werden kann:"
    )

    k_nearest_select_code = """
    import numpy as np
    from scipy.stats import mode

    points = [(0,1), (1,1), (3,4), (1,5), (1,2)]
    classes = ["A", "B", "C", "A", "C"]
    distances = [2,1,5,4,3]
    k = 2

    # Zip in Liste umwandeln
    distance_to_points = list(zip(points, classes, distances))

    # Nach Distanz sortieren
    distance_to_points.sort(key=lambda pointxdistance: pointxdistance[2])

    # k nächste Nachbarn
    k_nearest_distances = distance_to_points[:k]
    """
    st.code(k_nearest_select_code, line_numbers=True)

    st.markdown("#### 3. Majority Vote")
    st.markdown(
        """
        Die finale Klassifikation erfolgt durch **Mehrheitsentscheidung**.
        Die Klasse, die unter den k-nächsten Nachbarn am häufigsten vorkommt, gewinnt.

        **Beispiel:** Bei k=5 mit 3× Klasse A und 2× Klasse B → Ergebnis: **Klasse A**

        Der Modus (häufigster Wert) wird berechnet und als Klasse zugewiesen.
        """
    )

    majority_vote_code = """
    # Klassen der k-Nächsten
    k_classes = np.array([obj[1] for obj in k_nearest_distances])

    # Mehrheit bestimmen
    majority_class = mode(k_classes).mode[0]

    print(f"The classified class is {majority_class}")
    """

    st.code(majority_vote_code)

    st.markdown("---")
    st.markdown("## Wie wählt man den besten Wert für k?")
    st.markdown(
        """
        Die Wahl von **k** ist entscheidend für die Performance:

        ### Kleines k (z.B. k=1)
        - ✅ Sehr flexibel, passt sich den Daten genau an
        - ❌ Anfällig für **Rauschen** und Ausreißer
        - ❌ Kann zu **Overfitting** führen

        ### Großes k (z.B. k=15)
        - ✅ Robuster gegen Rauschen
        - ✅ Glattere Entscheidungsgrenzen
        - ❌ Kann wichtige Details übersehen (**Underfitting**)

        ### Faustregel
        - Oft wird **k = √n** verwendet (n = Anzahl Trainingspunkte)
        - Bei **2 Klassen**: k sollte **ungerade** sein (vermeidet Gleichstand)
        - Am besten: **Cross-Validation** zur Bestimmung des optimalen k
        """
    )

    st.markdown("---")
    st.markdown("## Vor- und Nachteile von KNN")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### ✅ Vorteile")
        st.markdown(
            """
            - **Einfach zu verstehen** und zu implementieren
            - **Kein Training** notwendig
            - Funktioniert für **Klassifikation und Regression**
            - Kann **nicht-lineare** Entscheidungsgrenzen lernen
            """
        )

    with col_right:
        st.markdown("### ❌ Nachteile")
        st.markdown(
            """
            - **Langsam** bei großen Datensätzen
            - **Speicherintensiv** (alle Daten müssen gespeichert werden)
            - Empfindlich gegenüber **irrelevanten Features**
            - Benötigt **Feature-Skalierung** (Normalisierung)
            """
        )
