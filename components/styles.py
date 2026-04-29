import streamlit as st

def inject_styles():
    st.markdown("""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
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
        
        /* Material Symbols icon styling */
        .material-symbols-outlined {
            font-family: 'Material Symbols Outlined';
            font-weight: normal;
            font-style: normal;
            line-height: 1;
            letter-spacing: normal;
            text-transform: none;
            display: inline-block;
            white-space: nowrap;
            word-wrap: normal;
            direction: ltr;
            -webkit-font-feature-settings: 'liga';
            -webkit-font-smoothing: antialiased;
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }
        
        /* ═══════════════════════════════════════════════════ */
        /* Fix Streamlit's broken Material Icon (stIconMaterial) */
        /* ═══════════════════════════════════════════════════ */
        
        /* Force Material Symbols font on Streamlit's icon component */
        [data-testid="stIconMaterial"] {
            font-family: 'Material Symbols Outlined' !important;
            font-weight: normal !important;
            font-style: normal !important;
            font-size: 24px !important;
            line-height: 1 !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            display: inline-block !important;
            white-space: nowrap !important;
            word-wrap: normal !important;
            direction: ltr !important;
            -webkit-font-feature-settings: 'liga' !important;
            -webkit-font-smoothing: antialiased !important;
            font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
        }
        
        /* Fix sidebar collapse/expand button (existing fix) */
        [data-testid="stSidebarCollapseButton"] span,
        [data-testid="stSidebarCollapsedControl"] span,
        button[kind="header"] span,
        [data-testid="collapsedControl"] span {
            font-size: 0 !important;
            visibility: hidden;
            position: relative;
        }
        
        [data-testid="stSidebarCollapseButton"] span::before,
        [data-testid="stSidebarCollapsedControl"] span::before,
        button[kind="header"] span::before,
        [data-testid="collapsedControl"] span::before {
            content: "»";
            font-size: 22px;
            visibility: visible;
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            color: #64748B;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
        
        [data-testid="stSidebar"][aria-expanded="true"] [data-testid="stSidebarCollapseButton"] span::before {
            content: "«";
        }
    </style>
    """, unsafe_allow_html=True)