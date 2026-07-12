"""Zentrale Farbpalette für alle Visualisierungen.

Spiegelt die Design-Tokens der Landing Page (landing/styles.css) wider, damit
App und Website als ein Produkt wirken. Alle Seiten beziehen ihre Farben aus
diesem Modul – keine Seite definiert mehr ihre eigene Palette.
"""

# --- Flächen ---
CANVAS = "#0f1420"  # tiefster Hintergrund / Plot-Hintergrund
PANEL = "#161c2c"  # erhöhte Fläche
RULE = "#262e44"  # Trennlinien / Gitternetz
INK = "#edeff5"  # Primärtext
MUTED = "#8e96ac"  # Sekundärtext / neutrale Marker

# --- Signalfarben: durchgängige Zwei-Klassen-Konvention ---
SIGNAL = "#ff8a3d"  # Orange: erste Serie, Klasse A, aktueller Punkt
CONTRAST = "#46c9c0"  # Teal: zweite Serie, Klasse B, Accuracy
HIGHLIGHT = "#ffd166"  # Warmes Gelb: aktives Element (Nachbarn, Signalfluss)

# --- Semantische Gewichte ---
POSITIVE = "#46c9c0"  # positives Gewicht (Teal)
NEGATIVE = "#e5646e"  # negatives Gewicht (gedämpftes Rot)

# --- Plotly-Layout-Bausteine (dunkles, transparentes Diagramm auf App-Canvas) ---
PLOTLY_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": INK},
    "colorway": [SIGNAL, CONTRAST, HIGHLIGHT, MUTED],
}


def sequential(value: float) -> str:
    """Ordnet einer Aktivierung (0..1) eine Farbe aus der Palette zu."""
    if value < 0.3:
        return MUTED
    if value < 0.7:
        return CONTRAST
    return SIGNAL
