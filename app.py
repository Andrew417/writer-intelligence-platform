import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math
from datetime import datetime

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="PubIntel Dashboard",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================
# HELPER: Force high-contrast Plotly text
# ============================================
def set_plot_contrast(fig):
    try:
        fig.update_layout(
            font=dict(family="IBM Plex Sans", color="#0F172A"),
            legend=dict(font=dict(color="#0F172A")),
            paper_bgcolor="white",
            plot_bgcolor="white",
        )
        fig.update_xaxes(
            tickfont=dict(color="#0F172A"), title_font=dict(color="#0F172A")
        )
        fig.update_yaxes(
            tickfont=dict(color="#0F172A"), title_font=dict(color="#0F172A")
        )
        try:
            fig.update_coloraxes(colorbar_tickfont=dict(color="#0F172A"))
        except Exception:
            pass
    except Exception:
        pass


# ============================================
# CUSTOM CSS
# ============================================
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'IBM Plex Sans', sans-serif;
        color: #0F172A;
        background-color: #F8FAFC;
    }

    .block-container {
        padding-top: 4rem;
        padding-bottom: 0rem;
        max-width: 1280px;
    }

    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: visible;}

    /* KPI Card */
    .kpi-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        transition: box-shadow 0.2s;
    }
    .kpi-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .kpi-label { font-size: 12px; font-weight: 500; color: #334155; margin-bottom: 8px; }
    .kpi-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 30px; font-weight: 700; color: #0F172A;
        letter-spacing: -0.04em; line-height: 1;
    }
    .kpi-sub { font-size: 18px; font-family: 'IBM Plex Mono', monospace; color: #475569; margin-left: 4px; }
    .kpi-trend { font-size: 12px; font-weight: 500; color: #065F46; margin-top: 8px; }
    .kpi-trend-warn { font-size: 12px; font-weight: 500; color: #78350F; margin-top: 8px; }

    /* Section Card */
    .section-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .section-title { font-size: 15px; font-weight: 600; color: #0F172A; margin-bottom: 4px; }
    .section-subtitle { font-size: 12px; color: #475569; margin-bottom: 16px; }

    /* Alert items */
    .alert-item { display: flex; align-items: flex-start; gap: 12px; padding: 12px 0; border-bottom: 1px solid #F8FAFC; }
    .alert-dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; flex-shrink: 0; }
    .alert-dot-red { background: #F43F5E; }
    .alert-dot-yellow { background: #F59E0B; }
    .alert-dot-blue { background: #4F46E5; }
    .alert-text { font-size: 13px; color: #334155; line-height: 1.5; }
    .alert-time { font-size: 11px; color: #475569; margin-top: 4px; }

    /* Sentiment boxes */
    .sentiment-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-top: 16px; }
    .sentiment-box { background: #F8FAFC; border: 1px solid #F1F5F9; border-radius: 8px; padding: 10px; text-align: center; }
    .sentiment-value { font-family: 'IBM Plex Mono', monospace; font-size: 18px; font-weight: 700; }
    .sentiment-label { font-size: 9px; font-weight: 600; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; }

    /* Genre bar */
    .genre-row { display: flex; align-items: center; gap: 16px; margin-bottom: 12px; }
    .genre-name { width: 140px; font-size: 13px; font-weight: 500; color: #334155; flex-shrink: 0; }
    .genre-bar-bg { flex: 1; height: 8px; background: #F8FAFC; border-radius: 999px; overflow: hidden; }
    .genre-bar-fill { height: 100%; border-radius: 999px; }
    .genre-pct { width: 40px; text-align: right; font-size: 13px; font-weight: 700; font-family: 'IBM Plex Mono', monospace; color: #0F172A; }
    .genre-count { width: 36px; text-align: right; font-size: 12px; color: #475569; }

    /* Table styling */
    .book-table { width: 100%; border-collapse: collapse; }
    .book-table th {
        font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;
        color: #334155; padding: 12px 24px; border-bottom: 1px solid #E2E8F0;
        background: rgba(248,250,252,0.5); text-align: left;
    }
    .book-table td { padding: 16px 24px; border-bottom: 1px solid #E2E8F0; font-size: 13px; color: #0F172A; }
    .book-table tr:hover { background: #F8FAFC; }
    .book-title { font-weight: 500; color: #0F172A; }
    .book-author { font-size: 11px; color: #475569; }
    .sentiment-bar-bg {
        width: 48px; height: 4px; background: #E2E8F0; border-radius: 999px;
        overflow: hidden; display: inline-block; vertical-align: middle; margin-right: 8px;
    }
    .sentiment-bar-fill { height: 100%; border-radius: 999px; }

    /* Page header */
    .page-greeting { font-size: 26px; font-weight: 700; letter-spacing: -0.03em; color: #0F172A; margin-bottom: 4px; }
    .page-sub { font-size: 13px; color: #475569; }

    [data-testid="stMetricValue"] { font-family: 'IBM Plex Mono', monospace; }

    /* Sidebar radio nav styling */
    [data-testid="stSidebar"] .stRadio > div { display:flex; flex-direction:column; gap:6px; }
    [data-testid="stSidebar"] .stRadio label {
        display:flex; align-items:center; gap:10px; color: #0F172A; background: transparent;
        padding: 10px 12px; margin: 0; border-radius: 8px; cursor: pointer; font-weight:600; transition: background 0.12s, color 0.12s;
    }
    [data-testid="stSidebar"] .stRadio label:hover { background:#F1F5F9; }
    [data-testid="stSidebar"] .stRadio input:checked + label,
    [data-testid="stSidebar"] .stRadio label[aria-checked="true"] {
        background:#EEF2FF; color:#4F46E5; border-left: 4px solid #4F46E5; padding-left: 8px;
    }

    .stButton>button, .stDownloadButton>button {
        background: #4F46E5 !important; color: #ffffff !important;
        border-radius: 8px !important; padding: 0.5rem 0.8rem !important; border: none !important;
    }
    .stButton>button:hover, .stDownloadButton>button:hover { background: #4338CA !important; }

    .stSelectbox, .stMultiselect, .stMultiSelect { color: #0F172A; }

    /* Hidden gems table styling */
    .gems-table { width: 100%; border-collapse: collapse; margin-top: 12px; }
    .gems-table th {
        font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;
        color: #334155; padding: 10px 16px; border-bottom: 1px solid #E2E8F0;
        background: rgba(248,250,252,0.5); text-align: left;
    }
    .gems-table td { padding: 12px 16px; border-bottom: 1px solid #E2E8F0; font-size: 13px; color: #0F172A; }
    .gems-table tr:hover { background: #F8FAFC; }

    /* Review cards */
    .review-positive { background: #F0FDF4; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #10B981; font-size: 13px; color: #334155; }
    .review-negative { background: #FFF1F2; padding: 12px 16px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #F43F5E; font-size: 13px; color: #334155; }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================
# DUMMY DATA
# ============================================
GENRES = [
    "Fantasy", "Romance", "Thriller", "Sci-Fi", "Literary Fiction",
    "Horror", "Mystery", "Contemporary", "Historical Fiction", "Young Adult",
]

books = [
    {"title": "The Silent Echo", "author": "J.K. Rowling", "genre": "Fantasy", "rating": 4.8, "pages": 412, "year": 2021, "reviews": 124302, "pos": 0.85, "neu": 0.10, "neg": 0.05, "viral": 92},
    {"title": "Midnight Sun", "author": "Stephenie Meyer", "genre": "Romance", "rating": 4.2, "pages": 384, "year": 2019, "reviews": 54321, "pos": 0.60, "neu": 0.28, "neg": 0.12, "viral": 78},
    {"title": "Shadows of the Past", "author": "Dan Brown", "genre": "Thriller", "rating": 3.9, "pages": 410, "year": 2018, "reviews": 87234, "pos": 0.45, "neu": 0.35, "neg": 0.20, "viral": 65},
    {"title": "The Last Kingdom", "author": "Bernard Cornwell", "genre": "Historical Fiction", "rating": 4.5, "pages": 620, "year": 2016, "reviews": 43210, "pos": 0.75, "neu": 0.18, "neg": 0.07, "viral": 84},
    {"title": "Nightfall Protocol", "author": "Brandon Sanderson", "genre": "Sci-Fi", "rating": 4.4, "pages": 528, "year": 2022, "reviews": 99210, "pos": 0.78, "neu": 0.15, "neg": 0.07, "viral": 88},
    {"title": "House of Whispers", "author": "Stephen King", "genre": "Horror", "rating": 3.4, "pages": 498, "year": 2020, "reviews": 67210, "pos": 0.40, "neu": 0.25, "neg": 0.35, "viral": 55},
    {"title": "Quiet Rivers", "author": "Kazuo Ishiguro", "genre": "Literary Fiction", "rating": 4.0, "pages": 288, "year": 2015, "reviews": 23210, "pos": 0.58, "neu": 0.30, "neg": 0.12, "viral": 48},
    {"title": "Stranger Echoes", "author": "Gillian Flynn", "genre": "Mystery", "rating": 4.1, "pages": 352, "year": 2017, "reviews": 41321, "pos": 0.66, "neu": 0.22, "neg": 0.12, "viral": 71},
    {"title": "Summer Roads", "author": "Colleen Hoover", "genre": "Young Adult", "rating": 4.3, "pages": 320, "year": 2023, "reviews": 98210, "pos": 0.72, "neu": 0.20, "neg": 0.08, "viral": 90},
    {"title": "Clockwork Hearts", "author": "Dan Simmons", "genre": "Fantasy", "rating": 4.6, "pages": 710, "year": 2024, "reviews": 34210, "pos": 0.81, "neu": 0.14, "neg": 0.05, "viral": 95},
    {"title": "Neon Dusk", "author": "William Gibson", "genre": "Sci-Fi", "rating": 4.1, "pages": 390, "year": 2020, "reviews": 28310, "pos": 0.70, "neu": 0.20, "neg": 0.10, "viral": 72},
    {"title": "The Rosewood Affair", "author": "Nicholas Sparks", "genre": "Romance", "rating": 3.8, "pages": 310, "year": 2021, "reviews": 61200, "pos": 0.55, "neu": 0.30, "neg": 0.15, "viral": 60},
    {"title": "Bone Garden", "author": "Tess Gerritsen", "genre": "Mystery", "rating": 4.3, "pages": 420, "year": 2019, "reviews": 38900, "pos": 0.72, "neu": 0.18, "neg": 0.10, "viral": 76},
    {"title": "The Walled City", "author": "Hilary Mantel", "genre": "Historical Fiction", "rating": 4.7, "pages": 580, "year": 2017, "reviews": 19200, "pos": 0.80, "neu": 0.14, "neg": 0.06, "viral": 68},
    {"title": "After Everything", "author": "Sally Rooney", "genre": "Contemporary", "rating": 3.6, "pages": 260, "year": 2022, "reviews": 72100, "pos": 0.50, "neu": 0.32, "neg": 0.18, "viral": 58},
    {"title": "Starfall Academy", "author": "Sarah J. Maas", "genre": "Young Adult", "rating": 4.5, "pages": 440, "year": 2024, "reviews": 112300, "pos": 0.82, "neu": 0.12, "neg": 0.06, "viral": 94},
    {"title": "The Hollow Man", "author": "Paul Tremblay", "genre": "Horror", "rating": 3.7, "pages": 330, "year": 2021, "reviews": 29400, "pos": 0.42, "neu": 0.28, "neg": 0.30, "viral": 52},
    {"title": "Paper Kingdoms", "author": "Donna Tartt", "genre": "Literary Fiction", "rating": 4.2, "pages": 510, "year": 2018, "reviews": 31200, "pos": 0.65, "neu": 0.24, "neg": 0.11, "viral": 62},
]

books_df = pd.DataFrame(books)

# Topics / keywords per genre — ALL 10 genres covered
topics_by_genre = {
    "Fantasy": [("world building", 0.91), ("magic system", 0.86), ("character development", 0.78), ("plot twists", 0.63), ("slow burn", 0.48), ("epic scope", 0.42), ("lore", 0.38), ("chosen one", 0.31), ("quest", 0.27), ("dark fantasy", 0.22)],
    "Romance": [("chemistry", 0.89), ("slow burn", 0.72), ("emotional depth", 0.68), ("happy ending", 0.55), ("spicy scenes", 0.44), ("second chance", 0.40), ("banter", 0.36), ("angst", 0.30), ("forced proximity", 0.26), ("dual POV", 0.21)],
    "Thriller": [("plot twists", 0.88), ("suspense", 0.81), ("pacing", 0.64), ("unreliable narrator", 0.42), ("dark atmosphere", 0.39), ("red herring", 0.35), ("stakes", 0.30), ("tension", 0.28), ("cliffhangers", 0.24), ("cat and mouse", 0.20)],
    "Horror": [("atmosphere", 0.86), ("tension", 0.72), ("gore", 0.45), ("psychological", 0.51), ("jump scares", 0.33), ("dread", 0.40), ("isolation", 0.36), ("body horror", 0.28), ("cosmic horror", 0.24), ("haunting", 0.20)],
    "Sci-Fi": [("world building", 0.77), ("tech plausibility", 0.69), ("speculative ideas", 0.59), ("pace", 0.44), ("twists", 0.38), ("dystopia", 0.35), ("AI themes", 0.31), ("space opera", 0.27), ("time travel", 0.23), ("alien contact", 0.19)],
    "Literary Fiction": [("prose", 0.84), ("themes", 0.69), ("character study", 0.67), ("symbolism", 0.46), ("ambiguity", 0.30), ("introspection", 0.42), ("social commentary", 0.38), ("unreliable narrator", 0.32), ("melancholy", 0.26), ("experimental", 0.20)],
    "Mystery": [("red herring", 0.82), ("whodunit", 0.71), ("clues", 0.65), ("detective", 0.52), ("twist ending", 0.41), ("motive", 0.38), ("suspicion", 0.34), ("procedural", 0.28), ("cold case", 0.24), ("locked room", 0.19)],
    "Contemporary": [("relationships", 0.79), ("identity", 0.68), ("family", 0.61), ("growth", 0.49), ("realism", 0.37), ("mental health", 0.42), ("slice of life", 0.35), ("social media", 0.28), ("generational", 0.23), ("urban life", 0.18)],
    "Historical Fiction": [("historical accuracy", 0.85), ("atmosphere", 0.73), ("war", 0.61), ("culture", 0.48), ("research", 0.39), ("period detail", 0.44), ("political intrigue", 0.37), ("survival", 0.30), ("forbidden love", 0.25), ("dynasty", 0.20)],
    "Young Adult": [("coming of age", 0.88), ("first love", 0.74), ("identity", 0.66), ("friendship", 0.55), ("rebellion", 0.42), ("chosen one", 0.38), ("found family", 0.34), ("self discovery", 0.29), ("school setting", 0.24), ("adventure", 0.20)],
}

# Emotion distributions — ALL 10 genres covered
emotion_keys = ["Joy", "Anger", "Fear", "Surprise", "Sadness", "Trust", "Anticipation", "Disgust"]
emotion_by_genre = {
    "Fantasy": [30, 3, 8, 12, 6, 22, 15, 4],
    "Romance": [35, 4, 5, 10, 7, 25, 12, 2],
    "Thriller": [18, 8, 22, 10, 12, 15, 10, 5],
    "Horror": [12, 6, 40, 6, 10, 8, 10, 8],
    "Sci-Fi": [22, 5, 12, 14, 8, 20, 12, 7],
    "Literary Fiction": [25, 3, 6, 8, 20, 22, 8, 8],
    "Mystery": [20, 5, 15, 18, 8, 18, 12, 4],
    "Contemporary": [28, 4, 6, 8, 18, 20, 10, 6],
    "Historical Fiction": [22, 6, 10, 8, 14, 22, 12, 6],
    "Young Adult": [32, 5, 8, 10, 12, 18, 10, 5],
}

# Sample reviews per genre
sample_reviews = {
    "Fantasy": {
        "positive": [
            "Absolutely immersive — the world building is extraordinary.",
            "Characters felt real and I couldn't put it down.",
            "A magical slow burn that paid off beautifully.",
        ],
        "negative": [
            "Pacing felt uneven in the middle chapters.",
            "Too many subplots diluted the main story.",
            "Magic system was confusing and poorly explained.",
        ],
    },
    "Romance": {
        "positive": [
            "The chemistry between the leads was electric.",
            "Emotionally rich — I cried and laughed on the same page.",
            "Perfect slow burn with a satisfying ending.",
        ],
        "negative": [
            "Felt formulaic after the first act.",
            "The miscommunication trope was overused.",
            "Not enough depth to the side characters.",
        ],
    },
    "Thriller": {
        "positive": [
            "Kept me on the edge of my seat until the last page.",
            "The twist at the end was genuinely shocking.",
            "Masterful pacing — couldn't read fast enough.",
        ],
        "negative": [
            "The ending felt rushed and unsatisfying.",
            "Too many plot holes to overlook.",
            "Characters made unbelievably dumb decisions.",
        ],
    },
    "Horror": {
        "positive": [
            "Genuinely terrifying — I slept with the lights on.",
            "The atmosphere was thick and suffocating in the best way.",
            "Psychological horror done right.",
        ],
        "negative": [
            "Relied too heavily on cheap jump scares.",
            "Gore without substance gets boring fast.",
            "The ending ruined an otherwise great buildup.",
        ],
    },
    "Sci-Fi": {
        "positive": [
            "Thought-provoking concepts woven into a gripping narrative.",
            "The world felt lived-in and scientifically plausible.",
            "Best AI-themed novel I've read in years.",
        ],
        "negative": [
            "Too much exposition, not enough story.",
            "Characters felt like mouthpieces for ideas.",
            "Pacing dragged in the second half.",
        ],
    },
    "Literary Fiction": {
        "positive": [
            "The prose is stunning — every sentence is crafted.",
            "A quiet masterpiece about human connection.",
            "Made me think about life differently.",
        ],
        "negative": [
            "Beautiful writing but nothing actually happens.",
            "Too pretentious for its own good.",
            "I couldn't connect with any of the characters.",
        ],
    },
    "Mystery": {
        "positive": [
            "The clues were fair and the solution was brilliant.",
            "Classic whodunit with modern sensibility.",
            "Couldn't stop guessing until the reveal.",
        ],
        "negative": [
            "The killer's identity was obvious from chapter three.",
            "Too many red herrings made it feel contrived.",
            "The detective's backstory overshadowed the case.",
        ],
    },
    "Contemporary": {
        "positive": [
            "Felt like reading about real people I know.",
            "Beautifully captures modern relationships.",
            "Raw and honest portrayal of mental health.",
        ],
        "negative": [
            "Nothing memorable happens — just vibes.",
            "Characters were unlikeable with no redemption.",
            "Tried too hard to be relevant.",
        ],
    },
    "Historical Fiction": {
        "positive": [
            "Transported me completely to another era.",
            "The research behind this is extraordinary.",
            "History made vivid and deeply personal.",
        ],
        "negative": [
            "Felt more like a textbook than a novel.",
            "Anachronistic dialogue broke the immersion.",
            "The romance subplot felt forced.",
        ],
    },
    "Young Adult": {
        "positive": [
            "A coming-of-age story that resonates at any age.",
            "The friendship dynamics felt so authentic.",
            "Fast-paced, fun, and surprisingly deep.",
        ],
        "negative": [
            "The love triangle felt unnecessary.",
            "Protagonist made frustratingly immature decisions.",
            "Too predictable — seen this story a hundred times.",
        ],
    },
}

# Trends over years (2015-2025)
years = list(range(2015, 2026))
trends = {
    "Fantasy": [40, 42, 44, 46, 48, 50, 54, 58, 62, 67, 72],
    "Romance": [30, 31, 32, 34, 36, 38, 40, 43, 46, 50, 55],
    "Literary Fiction": [55, 53, 51, 50, 48, 46, 44, 42, 40, 37, 34],
    "Thriller": [45, 46, 46, 47, 47, 46, 46, 47, 47, 48, 48],
    "Sci-Fi": [15, 16, 17, 18, 18, 19, 20, 21, 22, 23, 24],
    "Horror": [20, 21, 22, 22, 23, 24, 26, 28, 30, 33, 36],
    "Mystery": [35, 35, 36, 36, 37, 37, 38, 38, 39, 39, 40],
    "Contemporary": [25, 26, 27, 28, 29, 30, 31, 32, 32, 33, 34],
    "Historical Fiction": [28, 28, 27, 27, 26, 26, 25, 25, 24, 24, 23],
    "Young Adult": [32, 34, 36, 38, 40, 42, 44, 47, 50, 54, 58],
}
trends_df = pd.DataFrame({"year": years})
for g, v in trends.items():
    trends_df[g] = v

# Hidden Gems Index
books_df["HGI"] = (books_df["pos"] * books_df["rating"]) / np.log(
    books_df["reviews"] + 2
)
books_df["cluster"] = pd.qcut(
    books_df["HGI"], q=3, labels=["Mainstream", "Rising", "Hidden Gem"]
)


# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    # Logo
    st.markdown(
        """
    <div style="display:flex; align-items:center; gap:12px; padding:8px 0 24px 0; border-bottom: 1px solid #F1F5F9; margin-bottom:20px;">
        <div style="width:28px; height:28px; background:linear-gradient(135deg, #4f46e5, #4338CA); border-radius:8px; display:flex; align-items:center; justify-content:center; color:white; font-size:14px;">✨</div>
        <span style="font-size:17px; font-weight:700; letter-spacing:-0.02em; color:#0F172A;">PubIntel</span>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p style='font-size:10px; font-weight:600; letter-spacing:0.1em; color:#475569; text-transform:uppercase; padding-left:4px; margin-bottom:8px;'>Analytics</p>",
        unsafe_allow_html=True,
    )

    # Clean navigation mapping
    page_map = {
        "✨ Dashboard": "Dashboard",
        "📖 Book Insights": "Book Insights",
        "📊 Genre Analysis": "Genre Analysis",
        "📈 Market Trends": "Market Trends",
        "🔮 Rating Predictor": "Rating Predictor",
        "💎 Hidden Gems": "Hidden Gems",
    }

    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"

    # Find current index
    page_keys = list(page_map.keys())
    page_values = list(page_map.values())
    try:
        idx = page_values.index(st.session_state.page)
    except ValueError:
        idx = 0

    sel = st.radio("Nav", page_keys, index=idx, label_visibility="collapsed")
    page = page_map[sel]
    st.session_state.page = page

    # User profile at bottom
    st.markdown("---")
    st.markdown(
        """
    <div style="display:flex; align-items:center; gap:12px;">
        <div style="width:32px; height:32px; border-radius:50%; background:#EEF2FF; color:#4F46E5; font-weight:600; font-size:12px; display:flex; align-items:center; justify-content:center;">SC</div>
        <div>
            <p style="font-size:13px; font-weight:500; color:#0F172A; margin:0; line-height:1.3;">Sarah Chen</p>
            <span style="font-size:10px; font-weight:600; color:#065F46; background:#D1FAE5; padding:2px 8px; border-radius:999px;">Pro Plan</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# ============================================
# PAGE: DASHBOARD
# ============================================
if page == "Dashboard":

    st.markdown(
        """
    <div style="margin-bottom:8px;">
        <div class="page-greeting">Good morning, Sarah Chen ☀️</div>
        <div class="page-sub">Your publishing intelligence overview · Jun 2025</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # KPI CARDS
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(
            """
        <div class="kpi-card">
            <div class="kpi-label">📚 Books Analyzed</div>
            <div class="kpi-value">2,360,655</div>
            <div class="kpi-trend">▲ From Goodreads + UCSD datasets</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with k2:
        st.markdown(
            """
        <div class="kpi-card">
            <div class="kpi-label">📝 Reviews Processed</div>
            <div class="kpi-value">15.7M</div>
            <div class="kpi-trend">▲ NLP pipeline complete</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with k3:
        st.markdown(
            """
        <div class="kpi-card">
            <div class="kpi-label">⭐ Avg. Rating</div>
            <div><span class="kpi-value">3.87</span><span class="kpi-sub">/5.0</span></div>
            <div class="kpi-trend">Across all genres</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with k4:
        st.markdown(
            """
        <div class="kpi-card">
            <div class="kpi-label">🏷️ Genres Covered</div>
            <div class="kpi-value">24</div>
            <div class="kpi-trend">▲ 10 primary + 14 sub-genres</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # MAIN GRID: 60/40
    left_col, right_col = st.columns([3, 2])

    # LEFT: Top Performing Books Table
    with left_col:
        # Build table rows from data
        table_books = books_df.nlargest(6, "viral")
        rows_html = ""
        for _, b in table_books.iterrows():
            sent_pct = int(b["pos"] * 100)
            if sent_pct >= 70:
                sent_color = "#10B981"
            elif sent_pct >= 50:
                sent_color = "#F59E0B"
            else:
                sent_color = "#F43F5E"

            if b["viral"] >= 85:
                trend_arrow = "▲"
                trend_color = "#10B981"
            elif b["viral"] >= 70:
                trend_arrow = "→"
                trend_color = "#475569"
            else:
                trend_arrow = "▼"
                trend_color = "#F43F5E"

            rows_html += f"""
            <tr>
                <td>
                    <div class="book-title">{b['title']}</div>
                    <div class="book-author">{b['author']}</div>
                </td>
                <td>{b['rating']:.1f}★</td>
                <td>
                    <div class="sentiment-bar-bg"><div class="sentiment-bar-fill" style="width:{sent_pct}%; background:{sent_color};"></div></div>
                    <span style="font-size:11px; font-family:'IBM Plex Mono',monospace; color:#475569;">{sent_pct}%</span>
                </td>
                <td style="font-family:'IBM Plex Mono',monospace;">{int(b['viral'])}</td>
                <td style="text-align:right; color:{trend_color};">{trend_arrow}</td>
            </tr>
            """

        st.markdown(
            f"""
        <div class="section-card">
            <div class="section-title">Top Performing Books</div>
            <div class="section-subtitle">Ranked by viral potential</div>
            <table class="book-table">
                <thead>
                    <tr>
                        <th>Title / Author</th>
                        <th>Rating</th>
                        <th>Sentiment</th>
                        <th>Viral</th>
                        <th style="text-align:right">Trend</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # RIGHT: Stacked Cards
    with right_col:
        # NLP Alerts
        st.markdown(
            """
        <div class="section-card" style="margin-bottom:20px;">
            <div class="section-title">Recent NLP Alerts</div>
            <div style="margin-top:12px;">
                <div class="alert-item">
                    <div class="alert-dot alert-dot-red"></div>
                    <div>
                        <div class="alert-text">"Shadows of the Past" pacing criticized in 18% of recent reviews.</div>
                        <div class="alert-time">2 hours ago</div>
                    </div>
                </div>
                <div class="alert-item">
                    <div class="alert-dot alert-dot-yellow"></div>
                    <div>
                        <div class="alert-text">Plot confusion detected in Chapter 12 of "Midnight Sun".</div>
                        <div class="alert-time">5 hours ago</div>
                    </div>
                </div>
                <div class="alert-item">
                    <div class="alert-dot alert-dot-blue"></div>
                    <div>
                        <div class="alert-text">"The Silent Echo" quote trending on BookTok — +312% mentions.</div>
                        <div class="alert-time">1 day ago</div>
                    </div>
                </div>
                <div class="alert-item" style="border-bottom:none;">
                    <div class="alert-dot alert-dot-yellow"></div>
                    <div>
                        <div class="alert-text">"Summer Roads" negative sentiment spike detected in YA segment.</div>
                        <div class="alert-time">1 day ago</div>
                    </div>
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Portfolio Sentiment
        avg_pos = int(books_df["pos"].mean() * 100)
        avg_neu = int(books_df["neu"].mean() * 100)
        avg_neg = 100 - avg_pos - avg_neu

        st.markdown(
            f"""
        <div class="section-card">
            <div class="section-title">Portfolio Sentiment</div>
            <div class="section-subtitle">Across {len(books_df)} tracked books</div>
            <div style="display:flex; align-items:center; gap:24px;">
                <div style="width:80px; height:80px; border-radius:50%; border:6px solid #10B981; display:flex; flex-direction:column; align-items:center; justify-content:center; flex-shrink:0;">
                    <span style="font-size:20px; font-weight:700; font-family:'IBM Plex Mono',monospace; color:#0F172A;">{avg_pos}%</span>
                    <span style="font-size:9px; font-weight:700; color:#10B981; text-transform:uppercase;">Pos</span>
                </div>
                <div style="flex:1; display:flex; flex-direction:column; gap:8px;">
                    <div style="display:flex; justify-content:space-between; font-size:11px;">
                        <span style="color:#334155;">🟢 Positive</span>
                        <span style="font-family:'IBM Plex Mono',monospace; font-weight:700; color:#0F172A;">{avg_pos}%</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:11px;">
                        <span style="color:#334155;">⚪ Neutral</span>
                        <span style="font-family:'IBM Plex Mono',monospace; font-weight:700; color:#0F172A;">{avg_neu}%</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:11px;">
                        <span style="color:#334155;">🔴 Negative</span>
                        <span style="font-family:'IBM Plex Mono',monospace; font-weight:700; color:#0F172A;">{avg_neg}%</span>
                    </div>
                </div>
            </div>
            <div class="sentiment-grid">
                <div class="sentiment-box">
                    <div class="sentiment-value" style="color:#10B981;">{avg_pos}%</div>
                    <div class="sentiment-label">Pos.</div>
                </div>
                <div class="sentiment-box">
                    <div class="sentiment-value" style="color:#475569;">{avg_neu}%</div>
                    <div class="sentiment-label">Neut.</div>
                </div>
                <div class="sentiment-box">
                    <div class="sentiment-value" style="color:#F43F5E;">{avg_neg}%</div>
                    <div class="sentiment-label">Neg.</div>
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # BOTTOM: Genre Distribution
    genre_counts = books_df["genre"].value_counts()
    total_books = len(books_df)
    genre_colors = {
        "Fantasy": "#4F46E5", "Romance": "#EC4899", "Thriller": "#F43F5E",
        "Sci-Fi": "#F59E0B", "Literary Fiction": "#8B5CF6", "Horror": "#0F172A",
        "Mystery": "#10B981", "Contemporary": "#06B6D4", "Historical Fiction": "#D97706",
        "Young Adult": "#7C3AED",
    }

    genre_bars_html = ""
    for genre_name, count in genre_counts.items():
        pct = int(count / total_books * 100)
        color = genre_colors.get(genre_name, "#94A3B8")
        genre_bars_html += f"""
        <div class="genre-row">
            <div class="genre-name">{genre_name}</div>
            <div class="genre-bar-bg"><div class="genre-bar-fill" style="width:{pct}%; background:{color};"></div></div>
            <div class="genre-pct">{pct}%</div>
            <div class="genre-count">({count})</div>
        </div>
        """

    st.markdown(
        f"""
    <div class="section-card">
        <div class="section-title">Genre Distribution — Tracked Portfolio</div>
        <div class="section-subtitle">Your {total_books} books across genre segments</div>
        {genre_bars_html}
    </div>
    """,
        unsafe_allow_html=True,
    )


# ============================================
# PAGE: BOOK INSIGHTS
# ============================================
elif page == "Book Insights":
    st.markdown(
        '<div class="page-greeting">📖 Book Insights</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-sub">Deep dive into individual book performance</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    book_choice = st.selectbox("Select a book", books_df["title"].tolist())
    book = books_df[books_df["title"] == book_choice].iloc[0]

    # Top info cards
    c1, c2, c3 = st.columns([3, 2, 2])
    with c1:
        st.markdown(
            f"""
        <div class="section-card">
            <div class="section-title">{book.title}</div>
            <div class="section-subtitle">by {book.author} · {book.genre} · {int(book.year)}</div>
            <div style='display:flex; gap:24px; margin-top:16px;'>
                <div>
                    <div style='font-family:IBM Plex Mono; font-size:28px; font-weight:700; color:#0F172A;'>{book.rating:.1f}</div>
                    <div style='color:#475569; font-size:12px;'>Avg Rating</div>
                </div>
                <div>
                    <div style='font-family:IBM Plex Mono; font-size:20px; font-weight:700; color:#0F172A;'>{int(book.reviews):,}</div>
                    <div style='color:#475569; font-size:12px;'>Reviews</div>
                </div>
                <div>
                    <div style='font-family:IBM Plex Mono; font-size:20px; font-weight:700; color:#0F172A;'>{int(book.pages)}</div>
                    <div style='color:#475569; font-size:12px;'>Pages</div>
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with c2:
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=["Positive", "Neutral", "Negative"],
                    values=[book.pos, book.neu, book.neg],
                    hole=0.55,
                    marker=dict(colors=["#10B981", "#94A3B8", "#F43F5E"]),
                    textfont=dict(color="#0F172A"),
                )
            ]
        )
        fig.update_layout(
            title=dict(text="Sentiment Breakdown", font=dict(size=14, color="#0F172A")),
            margin=dict(t=40, b=20, l=20, r=20),
            height=280,
            showlegend=True,
            legend=dict(font=dict(size=11, color="#0F172A")),
        )
        set_plot_contrast(fig)
        st.plotly_chart(fig, use_container_width=True)

    with c3:
        # Top keywords list
        kws = topics_by_genre.get(book.genre, [])[:5]
        kw_rows = ""
        for k, s in kws:
            bar_w = int(s * 100)
            kw_rows += f"""
            <div style='display:flex; align-items:center; gap:8px; padding:8px 0; border-bottom:1px solid #F1F5F9;'>
                <div style='flex:1; font-size:13px; color:#334155;'>{k}</div>
                <div style='width:60px; height:4px; background:#E2E8F0; border-radius:999px; overflow:hidden;'>
                    <div style='width:{bar_w}%; height:100%; background:#4F46E5; border-radius:999px;'></div>
                </div>
                <div style='font-family:IBM Plex Mono; font-size:11px; color:#475569; width:36px; text-align:right;'>{s:.2f}</div>
            </div>
            """
        st.markdown(
            f"""
        <div class="section-card">
            <div class="section-title">Top Keywords</div>
            <div class="section-subtitle">From reader reviews</div>
            {kw_rows}
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Keywords horizontal bar chart + Emotion radar side by side
    col_left, col_right = st.columns(2)

    with col_left:
        kw_df = pd.DataFrame(
            topics_by_genre.get(book.genre, []), columns=["keyword", "score"]
        )
        if not kw_df.empty:
            fig2 = px.bar(
                kw_df,
                x="score",
                y="keyword",
                orientation="h",
                color="score",
                color_continuous_scale=["#C7D2FE", "#4F46E5"],
            )
            fig2.update_layout(
                title=dict(
                    text=f"Keywords in {book.genre}",
                    font=dict(size=14, color="#0F172A"),
                ),
                margin=dict(t=40, b=20, l=20, r=20),
                height=400,
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False,
            )
            set_plot_contrast(fig2)
            st.plotly_chart(fig2, use_container_width=True)

    with col_right:
        em = emotion_by_genre.get(book.genre, emotion_by_genre["Fantasy"])
        fig3 = go.Figure()
        fig3.add_trace(
            go.Scatterpolar(
                r=em + [em[0]],
                theta=emotion_keys + [emotion_keys[0]],
                fill="toself",
                name=book.genre,
                fillcolor="rgba(79, 70, 229, 0.15)",
                line=dict(color="#4F46E5", width=2),
            )
        )
        fig3.update_layout(
            title=dict(
                text=f"Emotion Profile — {book.genre}",
                font=dict(size=14, color="#0F172A"),
            ),
            margin=dict(t=40, b=20, l=40, r=40),
            height=400,
            polar=dict(
                radialaxis=dict(visible=True, tickfont=dict(color="#475569")),
                angularaxis=dict(tickfont=dict(color="#0F172A")),
            ),
        )
        set_plot_contrast(fig3)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Sample Reviews
    genre_reviews = sample_reviews.get(book.genre, sample_reviews["Fantasy"])

    pos_html = ""
    for q in genre_reviews["positive"]:
        pos_html += f'<div class="review-positive">"{q}"</div>'

    neg_html = ""
    for q in genre_reviews["negative"]:
        neg_html += f'<div class="review-negative">"{q}"</div>'

    col_p, col_n = st.columns(2)
    with col_p:
        st.markdown(
            f"""
        <div class="section-card">
            <div class="section-title">💚 What Readers Love</div>
            <div class="section-subtitle">Top positive review themes</div>
            {pos_html}
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col_n:
        st.markdown(
            f"""
        <div class="section-card">
            <div class="section-title">❤️ What Readers Dislike</div>
            <div class="section-subtitle">Common criticism themes</div>
            {neg_html}
        </div>
        """,
            unsafe_allow_html=True,
        )


# ============================================
# PAGE: GENRE ANALYSIS
# ============================================
elif page == "Genre Analysis":
    st.markdown(
        '<div class="page-greeting">📊 Genre Analysis</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-sub">Sentiment, themes, and emotions by genre</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    genre = st.selectbox("Select genre", sorted(GENRES))
    gdf = books_df[books_df["genre"] == genre]

    if not gdf.empty:
        pos = float(gdf["pos"].mean())
        neu = float(gdf["neu"].mean())
        neg = float(gdf["neg"].mean())
    else:
        pos, neu, neg = 0.6, 0.25, 0.15

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    left, right = st.columns([2, 3])

    with left:
        # Sentiment pie
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=["Positive", "Neutral", "Negative"],
                    values=[pos, neu, neg],
                    hole=0.5,
                    marker_colors=["#10B981", "#94A3B8", "#F43F5E"],
                    textfont=dict(color="#0F172A"),
                )
            ]
        )
        fig.update_layout(
            title=dict(
                text=f"Sentiment — {genre}",
                font=dict(size=14, color="#0F172A"),
            ),
            margin=dict(t=40, b=20, l=20, r=20),
            height=320,
            legend=dict(font=dict(color="#0F172A")),
        )
        set_plot_contrast(fig)
        st.plotly_chart(fig, use_container_width=True)

        # Emotion radar
        em = emotion_by_genre.get(genre, emotion_by_genre["Fantasy"])
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatterpolar(
                r=em + [em[0]],
                theta=emotion_keys + [emotion_keys[0]],
                fill="toself",
                name=genre,
                fillcolor="rgba(139, 92, 246, 0.15)",
                line=dict(color="#8B5CF6", width=2),
            )
        )
        fig2.update_layout(
            title=dict(
                text=f"Emotion Profile — {genre}",
                font=dict(size=14, color="#0F172A"),
            ),
            margin=dict(t=40, b=20, l=40, r=40),
            height=350,
            polar=dict(
                radialaxis=dict(visible=True, tickfont=dict(color="#475569")),
                angularaxis=dict(tickfont=dict(color="#0F172A")),
            ),
        )
        set_plot_contrast(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    with right:
        # Topics bar chart
        topics = topics_by_genre.get(genre, [])
        if topics:
            tf = pd.DataFrame(topics, columns=["topic", "score"])
            fig3 = px.bar(
                tf,
                x="score",
                y="topic",
                orientation="h",
                color="score",
                color_continuous_scale=["#C7D2FE", "#4F46E5"],
            )
            fig3.update_layout(
                title=dict(
                    text=f"Top Topics in {genre}",
                    font=dict(size=14, color="#0F172A"),
                ),
                margin=dict(t=40, b=20, l=20, r=20),
                height=450,
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False,
            )
            set_plot_contrast(fig3)
            st.plotly_chart(fig3, use_container_width=True)

        # Books in this genre
        genre_books = books_df[books_df["genre"] == genre][
            ["title", "author", "rating", "reviews"]
        ].sort_values("rating", ascending=False)
        if not genre_books.empty:
            st.markdown(
                f"""
            <div class="section-card">
                <div class="section-title">Books in {genre}</div>
                <div class="section-subtitle">{len(genre_books)} books tracked</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            for _, gb in genre_books.iterrows():
                st.markdown(
                    f"""
                <div style='display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid #F1F5F9; font-size:13px;'>
                    <div><span style='font-weight:500;'>{gb['title']}</span> <span style='color:#475569;'>— {gb['author']}</span></div>
                    <div style='font-family:IBM Plex Mono; color:#0F172A;'>{gb['rating']:.1f}★</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Genre Comparison
    st.markdown(
        '<div class="section-card"><div class="section-title">Genre Comparison</div><div class="section-subtitle">Compare sentiment and emotions side by side</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    g1, g2 = st.columns(2)
    with g1:
        comp1 = st.selectbox("Compare genre A", sorted(GENRES), index=0, key="comp1")
    with g2:
        comp2 = st.selectbox("Compare genre B", sorted(GENRES), index=1, key="comp2")

    comp_col1, comp_col2 = st.columns(2)

    with comp_col1:
        # Sentiment comparison bar
        comp_data = []
        for comp_genre in [comp1, comp2]:
            cdf = books_df[books_df["genre"] == comp_genre]
            if not cdf.empty:
                comp_data.append({"genre": comp_genre, "Positive": cdf["pos"].mean(), "Neutral": cdf["neu"].mean(), "Negative": cdf["neg"].mean()})
            else:
                comp_data.append({"genre": comp_genre, "Positive": 0.5, "Neutral": 0.3, "Negative": 0.2})

        comp_df = pd.DataFrame(comp_data)
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(name="Positive", x=comp_df["genre"], y=comp_df["Positive"], marker_color="#10B981"))
        fig_comp.add_trace(go.Bar(name="Neutral", x=comp_df["genre"], y=comp_df["Neutral"], marker_color="#94A3B8"))
        fig_comp.add_trace(go.Bar(name="Negative", x=comp_df["genre"], y=comp_df["Negative"], marker_color="#F43F5E"))
        fig_comp.update_layout(
            barmode="group",
            title=dict(text="Sentiment Comparison", font=dict(size=14, color="#0F172A")),
            margin=dict(t=40, b=20, l=20, r=20),
            height=350,
        )
        set_plot_contrast(fig_comp)
        st.plotly_chart(fig_comp, use_container_width=True)

    with comp_col2:
        # Emotion comparison radar
        em1 = emotion_by_genre.get(comp1, emotion_by_genre["Fantasy"])
        em2 = emotion_by_genre.get(comp2, emotion_by_genre["Fantasy"])
        fig_em = go.Figure()
        fig_em.add_trace(
            go.Scatterpolar(r=em1 + [em1[0]], theta=emotion_keys + [emotion_keys[0]], fill="toself", name=comp1, fillcolor="rgba(79, 70, 229, 0.15)", line=dict(color="#4F46E5", width=2))
        )
        fig_em.add_trace(
            go.Scatterpolar(r=em2 + [em2[0]], theta=emotion_keys + [emotion_keys[0]], fill="toself", name=comp2, fillcolor="rgba(236, 72, 153, 0.15)", line=dict(color="#EC4899", width=2))
        )
        fig_em.update_layout(
            title=dict(text="Emotion Comparison", font=dict(size=14, color="#0F172A")),
            margin=dict(t=40, b=20, l=40, r=40),
            height=350,
            polar=dict(
                radialaxis=dict(visible=True, tickfont=dict(color="#475569")),
                angularaxis=dict(tickfont=dict(color="#0F172A")),
            ),
        )
        set_plot_contrast(fig_em)
        st.plotly_chart(fig_em, use_container_width=True)


# ============================================
# PAGE: MARKET TRENDS
# ============================================
elif page == "Market Trends":
    st.markdown(
        '<div class="page-greeting">📈 Market Trends</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-sub">Genre popularity and market gap analysis</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Genre popularity over years
    trend_colors = {
        "Fantasy": "#4F46E5", "Romance": "#EC4899", "Literary Fiction": "#8B5CF6",
        "Thriller": "#F43F5E", "Sci-Fi": "#F59E0B", "Horror": "#0F172A",
        "Mystery": "#10B981", "Contemporary": "#06B6D4",
        "Historical Fiction": "#D97706", "Young Adult": "#7C3AED",
    }

    selected_trends = st.multiselect(
        "Select genres to compare",
        sorted(trends.keys()),
        default=["Fantasy", "Romance", "Literary Fiction", "Thriller", "Young Adult"],
    )

    fig = go.Figure()
    for g in selected_trends:
        if g in trends_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=trends_df["year"],
                    y=trends_df[g],
                    mode="lines+markers",
                    name=g,
                    line=dict(color=trend_colors.get(g, "#94A3B8"), width=2),
                    marker=dict(size=6),
                )
            )
    fig.update_layout(
        title=dict(
            text="Genre Popularity Over Time (2015–2025)",
            font=dict(size=16, color="#0F172A"),
        ),
        xaxis_title="Year",
        yaxis_title="Relative Popularity Index",
        margin=dict(t=50, b=40, l=40, r=20),
        height=450,
        hovermode="x unified",
    )
    set_plot_contrast(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Growing vs Declining
    left_t, right_t = st.columns(2)

    with left_t:
        change = []
        for g in trends:
            start_val = trends[g][0]
            end_val = trends[g][-1]
            pct_change = ((end_val - start_val) / max(1, start_val)) * 100
            change.append({"genre": g, "change": round(pct_change, 1)})
        change_df = pd.DataFrame(change).sort_values("change", ascending=True)

        colors = [
            "#10B981" if x > 0 else "#F43F5E" for x in change_df["change"]
        ]

        fig2 = go.Figure(
            go.Bar(
                x=change_df["change"],
                y=change_df["genre"],
                orientation="h",
                marker_color=colors,
                text=[f"{x:+.1f}%" for x in change_df["change"]],
                textposition="outside",
                textfont=dict(color="#0F172A", size=11),
            )
        )
        fig2.update_layout(
            title=dict(
                text="Growth Rate (2015 → 2025)",
                font=dict(size=14, color="#0F172A"),
            ),
            margin=dict(t=40, b=20, l=20, r=60),
            height=450,
            xaxis_title="% Change",
        )
        set_plot_contrast(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    with right_t:
        # Market Gap Scatter
        agg = (
            books_df.groupby("genre")
            .agg(
                avg_rating=("rating", "mean"),
                num_books=("title", "count"),
                reviews_sum=("reviews", "sum"),
                pos_mean=("pos", "mean"),
            )
            .reset_index()
        )
        agg["bubble_size"] = agg["reviews_sum"] / 1000

        fig3 = px.scatter(
            agg,
            x="avg_rating",
            y="num_books",
            size="bubble_size",
            color="pos_mean",
            hover_name="genre",
            color_continuous_scale=["#F43F5E", "#F59E0B", "#10B981"],
            text="genre",
        )
        fig3.update_traces(textposition="top center", textfont=dict(size=10, color="#0F172A"))
        fig3.update_layout(
            title=dict(
                text="Market Gap Analysis",
                font=dict(size=14, color="#0F172A"),
            ),
            xaxis_title="Average Rating (Quality/Demand)",
            yaxis_title="Number of Books (Supply)",
            margin=dict(t=40, b=40, l=40, r=20),
            height=450,
            coloraxis_colorbar=dict(title="Sentiment"),
        )
        # Add quadrant annotation
        fig3.add_annotation(
            x=4.5,
            y=1,
            text="🎯 OPPORTUNITY<br>High quality, low supply",
            showarrow=False,
            font=dict(size=10, color="#4F46E5"),
            bgcolor="rgba(238,242,255,0.8)",
            borderpad=6,
        )
        set_plot_contrast(fig3)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Heatmap: genres × emotions
    st.markdown(
        '<div class="section-card" style="margin-bottom:8px;"><div class="section-title">Genre × Emotion Heatmap</div><div class="section-subtitle">Emotion intensity across genres</div></div>',
        unsafe_allow_html=True,
    )

    heat_genres = sorted(emotion_by_genre.keys())
    heat_vals = [emotion_by_genre[g] for g in heat_genres]

    fig4 = px.imshow(
        np.array(heat_vals),
        x=emotion_keys,
        y=heat_genres,
        color_continuous_scale="RdYlGn",
        aspect="auto",
        text_auto=True,
    )
    fig4.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        height=420,
        coloraxis_colorbar=dict(title="Intensity"),
    )
    set_plot_contrast(fig4)
    st.plotly_chart(fig4, use_container_width=True)


# ============================================
# PAGE: RATING PREDICTOR
# ============================================
elif page == "Rating Predictor":
    st.markdown(
        '<div class="page-greeting">🔮 Rating Predictor</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-sub">Predict how your next book will perform</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Explanation card
    st.markdown(
        """
    <div class="section-card" style="margin-bottom:16px;">
        <div class="section-title">How It Works</div>
        <div class="section-subtitle" style="margin-bottom:0;">
            Our regression model analyzes genre trends, page count, thematic elements, and target emotions 
            to predict how readers will rate your book. The model was trained on 15M+ reviews using 
            Linear Regression and Random Forest algorithms.
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Input form
    form_col, result_col = st.columns([1, 1])

    with form_col:
        st.markdown(
            '<div class="section-card"><div class="section-title">📝 Book Details</div><div class="section-subtitle">Enter your planned book characteristics</div></div>',
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        with st.form("predictor"):
            g = st.selectbox("Genre", sorted(GENRES))
            pages_input = st.slider("Number of pages", 100, 800, 320, step=10)
            all_themes = sorted(
                {k for vals in topics_by_genre.values() for k, _ in vals}
            )
            themes = st.multiselect(
                "Themes (select up to 5)", all_themes, max_selections=5
            )
            target_emotion = st.selectbox("Target primary emotion", emotion_keys)
            submitted = st.form_submit_button("🔮 Predict Rating")

    with result_col:
        if submitted:
            # Fake prediction formula
            base = 3.2
            genre_bonus_map = {
                "Fantasy": 0.4, "Romance": 0.3, "Thriller": 0.1, "Horror": -0.2,
                "Literary Fiction": -0.1, "Sci-Fi": 0.25, "Mystery": 0.15,
                "Contemporary": -0.05, "Historical Fiction": 0.2, "Young Adult": 0.35,
            }
            gb = genre_bonus_map.get(g, 0.0)
            pages_bonus = 0.2 if 250 <= pages_input <= 500 else -0.1
            theme_bonus = 0.05 * len(themes)
            emotion_bonus_map = {
                "Joy": 0.12, "Trust": 0.06, "Anticipation": 0.04,
                "Fear": -0.08, "Sadness": -0.05, "Anger": -0.06,
                "Surprise": 0.03, "Disgust": -0.08,
            }
            eb = emotion_bonus_map.get(target_emotion, 0)
            pred = base + gb + pages_bonus + theme_bonus + eb
            pred = max(1.5, min(4.9, pred))
            pred_rounded = round(pred, 1)

            # Classification
            if pred >= 4.2:
                label = "Highly Loved"
                label_color = "#10B981"
                label_bg = "#D1FAE5"
                label_icon = "🌟"
            elif pred >= 3.6:
                label = "Mixed Reception"
                label_color = "#F59E0B"
                label_bg = "#FEF3C7"
                label_icon = "⚡"
            else:
                label = "Needs Improvement"
                label_color = "#F43F5E"
                label_bg = "#FFE4E6"
                label_icon = "⚠️"

            st.markdown(
                f"""
            <div class="section-card" style="text-align:center;">
                <div class="section-title">Predicted Rating</div>
                <div style="margin-top:16px;">
                    <span style="font-family:'IBM Plex Mono',monospace; font-size:48px; font-weight:700; color:#0F172A;">{pred_rounded}</span>
                    <span style="font-size:24px; font-family:'IBM Plex Mono',monospace; color:#475569;">/5.0</span>
                </div>
                <div style="margin-top:12px;">
                    <span style="background:{label_bg}; color:{label_color}; padding:6px 16px; border-radius:999px; font-size:13px; font-weight:600;">
                        {label_icon} {label}
                    </span>
                </div>
                <div style="margin-top:16px; font-size:12px; color:#475569;">
                    Based on {g} genre · {pages_input} pages · {len(themes)} themes · {target_emotion} emotion
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            # Feature importance
            fi = pd.DataFrame(
                {
                    "feature": ["Genre", "Page Count", "Themes", "Emotion"],
                    "importance": [abs(gb), abs(pages_bonus), abs(theme_bonus), abs(eb)],
                }
            )
            total_imp = fi["importance"].sum()
            if total_imp > 0:
                fi["importance"] = fi["importance"] / total_imp
            fi = fi.sort_values("importance", ascending=True)

            figfi = go.Figure(
                go.Bar(
                    x=fi["importance"],
                    y=fi["feature"],
                    orientation="h",
                    marker_color=["#C7D2FE", "#93C5FD", "#6366F1", "#4F46E5"],
                    text=[f"{x:.0%}" for x in fi["importance"]],
                    textposition="outside",
                    textfont=dict(color="#0F172A", size=11),
                )
            )
            figfi.update_layout(
                title=dict(
                    text="Feature Importance",
                    font=dict(size=14, color="#0F172A"),
                ),
                margin=dict(t=40, b=20, l=20, r=60),
                height=280,
                xaxis=dict(tickformat=".0%"),
            )
            set_plot_contrast(figfi)
            st.plotly_chart(figfi, use_container_width=True)

        else:
            # Show placeholder before prediction
            st.markdown(
                """
            <div class="section-card" style="text-align:center; padding:60px 24px;">
                <div style="font-size:48px; margin-bottom:12px;">🔮</div>
                <div class="section-title" style="text-align:center;">Your Prediction Will Appear Here</div>
                <div class="section-subtitle" style="text-align:center; margin-bottom:0;">
                    Fill in your book details and click "Predict Rating" to see the results.
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )


# ============================================
# PAGE: HIDDEN GEMS
# ============================================
elif page == "Hidden Gems":
    st.markdown(
        '<div class="page-greeting">💎 Hidden Gems</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-sub">High quality books with untapped potential</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Explanation card
    st.markdown(
        """
    <div class="section-card" style="margin-bottom:16px;">
        <div class="section-title">What is a Hidden Gem?</div>
        <div class="section-subtitle" style="margin-bottom:8px;">
            Books that readers love but haven't reached mainstream popularity yet. 
            These represent untapped opportunities for publishers and marketing teams.
        </div>
        <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:12px 16px; font-family:'IBM Plex Mono',monospace; font-size:13px; color:#4F46E5;">
            HGI = (sentiment_score × rating) / log(review_count)
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Filters
    filter_col1, filter_col2 = st.columns([1, 3])
    with filter_col1:
        genre_filter = st.selectbox(
            "Filter by genre", ["All Genres"] + sorted(GENRES)
        )

    # Get gems
    gems = books_df.copy().sort_values("HGI", ascending=False)
    if genre_filter != "All Genres":
        gems = gems[gems["genre"] == genre_filter]

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Build HTML table for gems
    gems_rows = ""
    for rank, (_, row) in enumerate(gems.iterrows(), 1):
        # HGI badge color
        if row["HGI"] >= gems["HGI"].quantile(0.7):
            hgi_color = "#10B981"
            hgi_bg = "#D1FAE5"
        elif row["HGI"] >= gems["HGI"].quantile(0.4):
            hgi_color = "#F59E0B"
            hgi_bg = "#FEF3C7"
        else:
            hgi_color = "#475569"
            hgi_bg = "#F1F5F9"

        # Cluster badge
        cluster_colors = {
            "Hidden Gem": ("#4F46E5", "#EEF2FF"),
            "Rising": ("#F59E0B", "#FEF3C7"),
            "Mainstream": ("#475569", "#F1F5F9"),
        }
        cl_color, cl_bg = cluster_colors.get(
            row["cluster"], ("#475569", "#F1F5F9")
        )

        sent_pct = int(row["pos"] * 100)

        gems_rows += f"""
        <tr>
            <td style="font-family:'IBM Plex Mono',monospace; color:#475569; font-size:12px;">{rank}</td>
            <td>
                <div class="book-title">{row['title']}</div>
                <div class="book-author">{row['author']}</div>
            </td>
            <td><span style="background:#F1F5F9; padding:2px 8px; border-radius:999px; font-size:11px; color:#475569;">{row['genre']}</span></td>
            <td style="font-family:'IBM Plex Mono',monospace;">{row['rating']:.1f}★</td>
            <td style="font-family:'IBM Plex Mono',monospace;">{int(row['reviews']):,}</td>
            <td>
                <div class="sentiment-bar-bg" style="width:40px;"><div class="sentiment-bar-fill" style="width:{sent_pct}%; background:#10B981;"></div></div>
                <span style="font-size:11px; font-family:'IBM Plex Mono',monospace; color:#475569;">{sent_pct}%</span>
            </td>
            <td>
                <span style="background:{hgi_bg}; color:{hgi_color}; padding:2px 10px; border-radius:999px; font-size:12px; font-weight:600; font-family:'IBM Plex Mono',monospace;">
                    {row['HGI']:.3f}
                </span>
            </td>
            <td>
                <span style="background:{cl_bg}; color:{cl_color}; padding:2px 10px; border-radius:999px; font-size:11px; font-weight:600;">
                    {row['cluster']}
                </span>
            </td>
        </tr>
        """

    st.markdown(
        f"""
    <div class="section-card">
        <div class="section-title">Hidden Gem Rankings</div>
        <div class="section-subtitle">Sorted by Hidden Gem Index (HGI)</div>
        <table class="gems-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Title / Author</th>
                    <th>Genre</th>
                    <th>Rating</th>
                    <th>Reviews</th>
                    <th>Sentiment</th>
                    <th>HGI</th>
                    <th>Cluster</th>
                </tr>
            </thead>
            <tbody>
                {gems_rows}
            </tbody>
        </table>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Scatter plots side by side
    scatter_left, scatter_right = st.columns(2)

    with scatter_left:
        fig = px.scatter(
            gems,
            x=np.log1p(gems["reviews"]),
            y="rating",
            size="HGI",
            color="pos",
            hover_name="title",
            color_continuous_scale=["#F43F5E", "#F59E0B", "#10B981"],
            size_max=25,
        )
        fig.update_layout(
            title=dict(
                text="Rating vs Popularity",
                font=dict(size=14, color="#0F172A"),
            ),
            xaxis_title="log(Review Count)",
            yaxis_title="Rating",
            margin=dict(t=40, b=40, l=40, r=20),
            height=420,
            coloraxis_colorbar=dict(title="Sentiment"),
        )
        # Highlight gem zone
        fig.add_annotation(
            x=np.log1p(gems["reviews"].min()) + 0.5,
            y=gems["rating"].max() - 0.1,
            text="💎 Hidden Gem Zone",
            showarrow=False,
            font=dict(size=10, color="#4F46E5"),
            bgcolor="rgba(238,242,255,0.8)",
            borderpad=6,
        )
        set_plot_contrast(fig)
        st.plotly_chart(fig, use_container_width=True)

    with scatter_right:
        cluster_colors_map = {
            "Mainstream": "#94A3B8",
            "Rising": "#F59E0B",
            "Hidden Gem": "#4F46E5",
        }
        fig2 = px.scatter(
            books_df,
            x=np.log1p(books_df["reviews"]),
            y="rating",
            color="cluster",
            size="HGI",
            hover_name="title",
            color_discrete_map=cluster_colors_map,
            size_max=25,
        )
        fig2.update_layout(
            title=dict(
                text="Cluster Visualization",
                font=dict(size=14, color="#0F172A"),
            ),
            xaxis_title="log(Review Count)",
            yaxis_title="Rating",
            margin=dict(t=40, b=40, l=40, r=20),
            height=420,
        )
        set_plot_contrast(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Cluster descriptions
    st.markdown(
        """
    <div class="section-card">
        <div class="section-title">Cluster Descriptions</div>
        <div class="section-subtitle">What each segment means for publishers</div>
        <div style="display:flex; gap:16px; margin-top:12px;">
            <div style="flex:1; background:#F1F5F9; border-radius:8px; padding:16px; border-left:4px solid #94A3B8;">
                <div style="font-weight:600; font-size:13px; color:#0F172A; margin-bottom:4px;">📚 Mainstream</div>
                <div style="font-size:12px; color:#475569;">Well-known books with high review counts. Already discovered by readers — focus on maintaining momentum.</div>
            </div>
            <div style="flex:1; background:#FEF3C7; border-radius:8px; padding:16px; border-left:4px solid #F59E0B;">
                <div style="font-weight:600; font-size:13px; color:#0F172A; margin-bottom:4px;">📈 Rising</div>
                <div style="font-size:12px; color:#475569;">Growing readership with solid ratings. Good candidates for marketing investment and promotion pushes.</div>
            </div>
            <div style="flex:1; background:#EEF2FF; border-radius:8px; padding:16px; border-left:4px solid #4F46E5;">
                <div style="font-weight:600; font-size:13px; color:#0F172A; margin-bottom:4px;">💎 Hidden Gem</div>
                <div style="font-size:12px; color:#475569;">Exceptional quality but low visibility. Highest ROI potential — readers who find these books love them.</div>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )