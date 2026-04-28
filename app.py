import streamlit as st
st.set_page_config(page_title="PubIntel", page_icon="📊", layout="wide")
from components.styles import inject_styles
inject_styles()
st.title("📊 PubIntel")
st.caption("Editorial Intelligence Dashboard")
st.markdown("👈 Select a page from the sidebar.")