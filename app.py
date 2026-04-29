import streamlit as st
from components.styles import inject_styles

st.set_page_config(page_title="PubIntel", page_icon="📊", layout="wide")
inject_styles()

pages = [
	st.Page("pages/Dashboard.py", title="Dashboard", icon="📊", default=True),
	st.Page("pages/2_Book_Insights.py", title="Book Insights", icon="📘"),
	st.Page("pages/Genre_Analysis.py", title="Genre Analysis", icon="🧭"),
]

navigation = st.navigation(pages)
navigation.run()