"""Zentrale Farbpalette für alle Visualisierungen.

Spiegelt die Design-Tokens der Landing Page (landing/styles.css) wider, damit
App und Website als ein Produkt wirken. Alle Seiten beziehen ihre Farben aus
diesem Modul – keine Seite definiert mehr ihre eigene Palette.
"""

# --- Surfaces ---
CANVAS = "#0f1420"  # tiefster Hintergrund / Plot-Hintergrund
PANEL = "#161c2c"  # erhöhte Fläche
RULE = "#262e44"  # Trennlinien / Gitternetz
INK = "#edeff5"  # Primärtext
MUTED = "#8e96ac"  # Sekundärtext / neutrale Marker

# --- Signal colours: one consistent two-class convention ---
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


def with_alpha(hex_color: str, alpha: float) -> str:
    """Convert a `#rrggbb` token to `rgba(...)` at the given alpha.

    Lets Plotly annotation backgrounds (which need CSS-style rgba, not hex)
    stay tied to the palette instead of hardcoding a separate literal that
    silently drifts from PANEL/CANVAS when the palette changes.
    """
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"
