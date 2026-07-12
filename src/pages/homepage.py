import streamlit as st

st.title("ML Visualizer")

st.markdown(
    """
    Vier klassische Verfahren, jedes auf einer eigenen Seite, alles live gerechnet.

    Gradient Descent rollt eine Kugel in ein Minimum, und über die Lernrate entscheidest du,
    ob sie dort ankommt oder darüber hinausschießt. Das Perceptron lernt eine Trenngerade für
    die AND-Verknüpfung, ein Trainingsschritt nach dem anderen. KNN ordnet neue Punkte nach
    ihren nächsten Nachbarn ein, wobei k allein deine Entscheidung ist. Und das neuronale Netz
    lernt dieselbe AND-Funktion noch einmal, diesmal mit Hidden Layer und Backpropagation.

    Such dir links eine Seite aus. Interessant wird es meistens dort, wo die Parameter
    unvernünftig werden: Lernrate auf Anschlag, k größer als die halbe Punktwolke.
    """,
    unsafe_allow_html=True,
)
