import streamlit as st
import pandas as pd
from components.styles import inject_styles
from components.data import get_all_genres, get_genre_by_name, get_genre_names

inject_styles()


def fmt_percent(value):
    try:
        return f"{float(value) * 100:.0f}%"
    except Exception:
        return "0%"


def fmt_percent_signed(value):
    try:
        return f"{float(value) * 100:+.0f}%"
    except Exception:
        return "+0%"

# ═══════════════════════════════════════
# FETCH DATA FROM MONGODB
# ═══════════════════════════════════════

genre_names = get_genre_names()
all_genres_df = get_all_genres()

# ─── Genre Selector ───
selected_genre = st.selectbox(
    "Select a genre to analyze",
    genre_names,
    index=0,
    label_visibility="collapsed"
)

# Fetch the selected genre's full document
genre_doc = get_genre_by_name(selected_genre)

# ═══════════════════════════════════════
# MAP MONGO FIELDS → DISPLAY VALUES
# ═══════════════════════════════════════

# Emotion color mapping
EMOTION_COLORS = {
    "joy":      {"color": "#F59E0B", "bg": "#FEF3C7", "icon": "😊"},
    "anger":    {"color": "#EF4444", "bg": "#FEE2E2", "icon": "😡"},
    "sadness":  {"color": "#6B8DAE", "bg": "#E0EAF2", "icon": "😢"},
    "fear":     {"color": "#7C3AED", "bg": "#EDE9FE", "icon": "😨"},
    "surprise": {"color": "#14B8A6", "bg": "#CCFBF1", "icon": "😲"},
}

# Build emotion data from the mongo document
emotions = {}
for emo_key in ["joy", "anger", "sadness", "fear", "surprise"]:
    avg_key = f"avg_{emo_key}"
    value = genre_doc.get(avg_key, 0)
    ec = EMOTION_COLORS[emo_key]
    emotions[f"{ec['icon']} {emo_key.capitalize()}"] = {
        "value": value,
        "color": ec["color"],
        "bg": ec["bg"],
    }

# Find dominant (highest value)
dominant_key = genre_doc.get("genre_dominant_emotion", "joy")
dominant_color_info = EMOTION_COLORS.get(dominant_key, EMOTION_COLORS["joy"])

# Mark primary in emotions dict
for emo_name, emo_data in emotions.items():
    emo_data["primary"] = dominant_key.lower() in emo_name.lower()

# Sort emotions by value descending
emotions = dict(sorted(emotions.items(), key=lambda x: x[1]["value"], reverse=True))


# ═══════════════════════════════════════
# KPI ROW
# ═══════════════════════════════════════

st.markdown(f"## {selected_genre}")
st.caption(f"{genre_doc.get('total_books', 'N/A')} books · Dominant emotion: {dominant_color_info['icon']} {dominant_key.capitalize()}")

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Satisfaction",  fmt_percent(genre_doc.get('avg_satisfaction', 0)))
k2.metric("Engagement",    fmt_percent(genre_doc.get('avg_engagement_depth', 0)))
k3.metric("Value",         fmt_percent(genre_doc.get('avg_bang_for_buck', 0)))
k4.metric("Hype",          fmt_percent(genre_doc.get('avg_viral_potential', 0)))
k5.metric("Legacy",        fmt_percent(genre_doc.get('avg_timelessness', 0)))
k6.metric("Complexity",    fmt_percent(genre_doc.get('avg_emotional_complexity', 0)))

st.markdown("---")


# ═══════════════════════════════════════
# EMOTION FINGERPRINT
# ═══════════════════════════════════════

emo_left, emo_right = st.columns([7, 5], gap="large")

with emo_left:
    st.markdown("### Emotion Fingerprint")
    st.caption(f"NLP emotion distribution across {genre_doc.get('total_books', 0)} books")
    # Build a single-line HTML string for all emotion bars (semantic colors)
    bars_html = ""
    for emo_name, emo_data in emotions.items():
        primary_badge = ""
        if emo_data.get("primary"):
            primary_badge = f'<span style="font-size:9px; font-weight:700; padding:2px 8px; border-radius:999px; background:{emo_data["bg"]}; color:{emo_data["color"]}; margin-left:6px;">PRIMARY</span>'

        # clamp width between 0 and 100
        try:
            pct = max(0, min(100, float(emo_data["value"]) * 100))
        except Exception:
            pct = 0

        bars_html += (
            f'<div style="margin-bottom:14px;">'
            f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">'
            f'<span style="font-size:13px; font-weight:600; color:inherit;">{emo_name}{primary_badge}</span>'
            f'<span style="font-family:ui-monospace,monospace; font-weight:700; color:{emo_data["color"]};">{fmt_percent(emo_data["value"])}</span>'
            f'</div>'
            f'<div style="width:100%; height:10px; border-radius:999px; overflow:hidden; background:{emo_data["bg"]};">'
            f'<div style="height:100%; width:{pct}%; border-radius:999px; background:{emo_data["color"]};"></div>'
            f'</div>'
            f'</div>'
        )

    st.markdown(bars_html, unsafe_allow_html=True)

with emo_right:
    # Keep dominant card as a single safe HTML block
    st.markdown(f"""
    <div style="background:#0F172A; border-radius:16px; padding:40px 32px; min-height:400px; display:flex; flex-direction:column; justify-content:flex-end;">
        <div style="font-size:32px; margin-bottom:16px;">{dominant_color_info['icon']}</div>
        <span style="background:{dominant_color_info['color']}; color:white; font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; padding:4px 14px; border-radius:999px; width:fit-content; display:inline-block;">Dominant Emotion</span>
        <h1 style="color:white; font-size:48px; font-weight:800; margin:8px 0;">{dominant_key.capitalize()}</h1>
        <p style="color:#94A3B8; font-size:13px; margin-top:12px; line-height:1.7;">The defining psychological experience for {selected_genre} readers, based on NLP analysis of all reviews in the database.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# ═══════════════════════════════════════
# SENTIMENT ROW
# ═══════════════════════════════════════

s1, s2, s3 = st.columns(3, gap="large")

with s1:
    st.markdown("### Sentiment")
    st.caption("The Positivity Metric")
    sentiment_val = genre_doc.get("avg_sentiment", 0)
    st.metric("Score", fmt_percent_signed(sentiment_val), label_visibility="collapsed")

    # Use native progress bar for sentiment spectrum
    normalized = (sentiment_val + 1) / 2
    try:
        st.progress(float(normalized))
    except Exception:
        st.progress(0.5)
    left_label, right_label = st.columns(2)
    left_label.caption("Negative")
    right_label.caption("Positive")

with s2:
    st.markdown("### Sentiment Strength")
    st.caption("The Intensity Metric")
    strength_val = genre_doc.get("avg_sentiment_strength", 0)
    st.metric("Score", fmt_percent(strength_val), label_visibility="collapsed")

with s3:
    st.markdown("### Emotional Complexity")
    st.caption("The Rollercoaster Metric")
    complexity_val = genre_doc.get("avg_emotional_complexity", 0)
    st.metric("Score", fmt_percent(complexity_val), label_visibility="collapsed")

st.markdown("---")


# ═══════════════════════════════════════
# CULTURAL POSITIONING MATRIX
# ═══════════════════════════════════════

st.markdown("### Cultural Positioning Matrix")
st.caption("Cross-genre comparison · Selected genre highlighted")

# Build the matrix from ALL genres
matrix_data = []
for _, row in all_genres_df.iterrows():
    matrix_data.append({
        "Genre": row.get("genres", ""),
        "Books": int(row.get("total_books", 0)),
        "Satisfaction": round(row.get("avg_satisfaction", 0) * 100, 0),
        "Engagement": round(row.get("avg_engagement_depth", 0) * 100, 0),
        "Complexity": round(row.get("avg_emotional_complexity", 0) * 100, 0),
        "Intensity": round(row.get("avg_sentiment_strength", 0) * 100, 0),
        "Dominant": row.get("genre_dominant_emotion", "N/A").capitalize()
    })

matrix_df = pd.DataFrame(matrix_data)

# Sort by satisfaction descending
matrix_df = matrix_df.sort_values("Satisfaction", ascending=False).reset_index(drop=True)

st.dataframe(
    matrix_df,
    use_container_width=True,
    hide_index=True,
    height=500,
    column_config={
        "Genre": st.column_config.TextColumn("Genre", width="medium"),
        "Books": st.column_config.NumberColumn("Books", width="small"),
        "Satisfaction": st.column_config.ProgressColumn("Satisfaction", min_value=0, max_value=100, format="%.0f%%"),
        "Engagement": st.column_config.ProgressColumn("Engagement", min_value=0, max_value=100, format="%.0f%%"),
        "Complexity": st.column_config.ProgressColumn("Complexity", min_value=0, max_value=100, format="%.0f%%"),
        "Intensity": st.column_config.ProgressColumn("Intensity", min_value=0, max_value=100, format="%.0f%%"),
        "Dominant": st.column_config.TextColumn("Dominant", width="small"),
    }
)

st.caption(f"Showing {len(matrix_df)} genres · Minimum 5 books for statistical validity")

st.markdown("---")

# ═══════════════════════════════════════
# AI INSIGHT BAR
# ═══════════════════════════════════════

insight_col1, insight_col2 = st.columns([1, 15])
with insight_col1:
    st.markdown("### 🧠")
with insight_col2:
    st.markdown(f"**AI Insight for {selected_genre}**")
    metrics = {
        "Satisfaction": genre_doc.get("avg_satisfaction", 0),
        "Engagement": genre_doc.get("avg_engagement_depth", 0),
        "Value": genre_doc.get("avg_bang_for_buck", 0),
        "Viral Potential": genre_doc.get("avg_viral_potential", 0),
        "Timelessness": genre_doc.get("avg_timelessness", 0),
        "Emotional Complexity": genre_doc.get("avg_emotional_complexity", 0),
    }
    best_metric = max(metrics, key=metrics.get)
    best_value = metrics[best_metric]
    st.markdown(
        f"This genre's strongest dimension is **{best_metric}** at **{fmt_percent(best_value)}**. Its dominant emotion is **{dominant_key.capitalize()}**, derived from NLP analysis of reader reviews across **{genre_doc.get('total_books', 0)} books** in the database."
    )