import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        :root, [data-theme="light"], [data-theme="light"] body {
            color-scheme: light;
            --text-primary: #0F172A;
            --text-muted: #64748B;
            --text-value: #0F172A;
        }
    </style>
    """, unsafe_allow_html=True)