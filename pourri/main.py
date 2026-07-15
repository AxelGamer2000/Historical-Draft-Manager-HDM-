import streamlit as st

tabs_content = ["Attacking Trios", "Defenders Pairs", "Reserve", "Modify", "Search"]

tabs_sidebar = st.sidebar.radio(
    "Draft Manager",
    tabs_content
)

st.set_page_config(layout="wide")

# 2. On injecte le style CSS requis ET l'iframe directement dans st.markdown
st.markdown(
    """
    <style>
        /* Cible la boîte Streamlit qui englobe l'iframe pour la forcer à s'étirer */
        .stElementContainer iframe {
            height: 85vh !important;
            width: 100% !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

if tabs_sidebar == tabs_content[0]:
    pass
elif tabs_sidebar == tabs_content[4]:
    st.iframe("https://www.hockey-reference.com")