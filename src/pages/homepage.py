import streamlit as st

st.title("Startseite")

st.markdown(
    """
    **Willkommen zur Datascience & Artificial Intelligence Webanwendung**

    Diese interaktive App demonstriert grundlegende Konzepte und Visualisierungen aus dem Bereich
    der Datenwissenschaft und künstlichen Intelligenz. Du findest hier praktische, interaktive
    Seiten zu folgenden Themen:

    - **Gradient Descent** - Visualisierung des Lernprozesses und Einfluss der Lernrate
    - **Perceptron** - Einfache binäre Klassifikation mit Entscheidungsgrenzen
    - **KNN Visualizer** - Verstehen, wie Nachbarschafts-Klassifikation funktioniert
    - **Neuronale Netze** - Einfache neuronale Netz-Experimente und Visualisierungen

    Wähle eine Seite links in der Navigation, um loszulegen. Alle Beispiele sind für Lehrzwecke
    ausgelegt und ermöglichen das Verändern von Parametern zur Beobachtung des Verhaltens.
    """,
    unsafe_allow_html=True,
)
