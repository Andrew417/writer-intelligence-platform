import streamlit as st
import pandas as pd
import textwrap
from components.database import get_database
from components.styles import inject_styles

st.set_page_config(page_title="Book Insights", layout="wide")
inject_styles()

# Handle direct book deep-links from Dashboard
query_params = st.query_params
url_book_id = query_params.get("book_id", None)

# If we have a deep-link, ensure filters don't hide the book
if url_book_id and "deep_link_handled" not in st.session_state:
    st.session_state.deep_link_handled = True
    # Clear any filter session state to show all books
    for key in list(st.session_state.keys()):
        if key not in ("deep_link_handled",):
            try:
                del st.session_state[key]
            except Exception:
                pass

text_primary = "var(--text-primary)"
text_muted = "var(--text-muted)"
text_value = "var(--text-value)"


# ═══════════════════════════════════════
# Helpers
# ═══════════════════════════════════════

EMOTION_COLORS = {
    "joy":      {"color": "#F59E0B", "bg": "#FEF3C7", "icon": "😊"},
    "anger":    {"color": "#EF4444", "bg": "#FEE2E2", "icon": "😡"},
    "sadness":  {"color": "#6B8DAE", "bg": "#E0EAF2", "icon": "😢"},
    "fear":     {"color": "#7C3AED", "bg": "#EDE9FE", "icon": "😨"},
    "surprise": {"color": "#14B8A6", "bg": "#CCFBF1", "icon": "😲"},
}


@st.cache_data(ttl=600)
def fetch_all_books():
    db = get_database()
    cursor = db["books"].find({}, {
        "_id": 0,
        "book_id": 1,
        "title": 1,
        "author": 1,
        "genres": 1,
    })
    return list(cursor)


@st.cache_data(ttl=600)
def fetch_book_by_id(book_id: str):
    db = get_database()
    book = db["books"].find_one({"book_id": book_id}, {"_id": 0}) or {}
    emotion = db["book_emotion_summary"].find_one({"book_id": book_id}, {"_id": 0}) or {}
    viral = db["viral_proxy_metrics"].find_one({"book_id": book_id}, {"_id": 0}) or {}
    # Merge
    merged = {**book, **emotion, **viral}
    return merged


def fmt(n):
    try:
        return f"{n:.2f}"
    except Exception:
        return "0.00"


def fmt_percent(n):
    try:
        return f"{float(n) * 100:.1f}%"
    except Exception:
        return "0.0%"


def format_count(count):
    try:
        count = int(float(str(count).replace(",", "")))
    except (ValueError, TypeError):
        return str(count)
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)


def render_html(html: str) -> None:
    st.markdown(textwrap.dedent(html).strip(), unsafe_allow_html=True)


# ═══════════════════════════════════════
# Page: Book Insights
# ═══════════════════════════════════════

@st.cache_data(ttl=600)
def get_all_books_for_search():
    db = get_database()
    books_cursor = db["books"].find({}, {
        "_id": 0, "book_id": 1, "title": 1, "author": 1,
        "genres": 1, "rating_count": 1,
        "true_satisfaction": 1, "engagement_depth_score": 1,
        "normalized_bang_for_buck": 1, "normalized_timelessness": 1
    })
    books_df = pd.DataFrame(list(books_cursor))

    viral_cursor = db["viral_proxy_metrics"].find({}, {
        "_id": 0, "book_id": 1, "viral_potential_score": 1, "viral_label": 1
    })
    viral_df = pd.DataFrame(list(viral_cursor))

    if not books_df.empty and not viral_df.empty:
        merged = pd.merge(books_df, viral_df, on="book_id", how="left")
    else:
        merged = books_df
    return merged


all_books_df = get_all_books_for_search()
if all_books_df.empty:
    st.error("No books found in the database.")
    st.stop()

# build genres list
all_genres = set()
if "genres" in all_books_df.columns:
    for genres_list in all_books_df["genres"].dropna():
        if isinstance(genres_list, list):
            all_genres.update(genres_list)
sorted_genre_list = sorted(all_genres)


# --- Search + Filters (Option A) ---
search_query = st.text_input(
    "🔍 Search books by title or author...",
    placeholder="Type to search — e.g. 'Gone Girl' or 'Stephen King'",
    label_visibility="collapsed"
)

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([2, 2, 2, 6])

with filter_col1:
    genre_filter = st.selectbox(
        "Genre",
        options=["All Genres"] + sorted_genre_list,
        label_visibility="collapsed"
    )

with filter_col2:
    sort_by = st.selectbox(
        "Sort",
        options=[
            "Rating Count ↓",
            "Title (A-Z)",
            "True Satisfaction ↓",
            "Engagement Depth ↓",
            "Viral Potential ↓",
            "Bang for Buck ↓",
            "Timelessness ↓"
        ],
        label_visibility="collapsed"
    )

with filter_col3:
    viral_filter = st.selectbox(
        "Viral Label",
        options=["All", "🔥 High", "⚡ Moderate", "💤 Low"],
        label_visibility="collapsed"
    )

# Apply filters
filtered_df = all_books_df.copy()
if search_query:
    q = search_query.lower()
    if "title" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["title"].fillna("").str.lower().str.contains(q, na=False) |
                                  filtered_df["author"].fillna("").str.lower().str.contains(q, na=False)]

if genre_filter != "All Genres":
    if "genres" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["genres"].apply(lambda g: genre_filter in g if isinstance(g, list) else False)]

if viral_filter != "All":
    label_map = {"🔥 High": "High Viral Potential", "⚡ Moderate": "Moderate Viral Potential", "💤 Low": "Low Viral Potential"}
    if "viral_label" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["viral_label"] == label_map.get(viral_filter, viral_filter)]

sort_map = {
    "Title (A-Z)": ("title", True),
    "True Satisfaction ↓": ("true_satisfaction", False),
    "Engagement Depth ↓": ("engagement_depth_score", False),
    "Viral Potential ↓": ("viral_potential_score", False),
    "Bang for Buck ↓": ("normalized_bang_for_buck", False),
    "Timelessness ↓": ("normalized_timelessness", False),
    "Rating Count ↓": ("rating_count", False),
}
sort_col, sort_asc = sort_map.get(sort_by, ("rating_count", False))
if sort_col in filtered_df.columns:
    try:
        filtered_df = filtered_df.sort_values(sort_col, ascending=sort_asc).reset_index(drop=True)
    except Exception:
        filtered_df = filtered_df.reset_index(drop=True)
else:
    filtered_df = filtered_df.reset_index(drop=True)

st.caption(f"Showing {len(filtered_df)} of {len(all_books_df)} books")

if len(filtered_df) == 0:
    st.warning("No books found matching your search.")
    st.stop()

# Create display labels and selection
# Create display labels
book_options = filtered_df.apply(lambda r: f"{r.get('title','Untitled')} — {r.get('author','')}", axis=1).tolist()

# Check URL for ?book_id=... and pre-select that book
default_index = 0
query_params = st.query_params
url_book_id = query_params.get("book_id", None)

if url_book_id:
    matching_rows = filtered_df[filtered_df["book_id"].astype(str) == str(url_book_id)]
    if not matching_rows.empty:
        # Find the position of this book in the filtered list
        matched_idx = matching_rows.index[0]
        try:
            default_index = filtered_df.index.get_loc(matched_idx)
        except KeyError:
            default_index = 0

selected_book_label = st.selectbox(
    "Select a book from results", 
    options=book_options, 
    index=default_index,
    label_visibility="collapsed"
)
selected_index = book_options.index(selected_book_label)
selected_book_id = filtered_df.iloc[selected_index]["book_id"]

# fetch the merged book record for the selected book
book = fetch_book_by_id(selected_book_id)

title = book.get("title", "Untitled")
author = book.get("author", "Unknown")
publish = book.get("publish_date", "")
genres = book.get("genres", []) or []

# Determine emotions
dominant = (book.get("dominant_emotion") or book.get("genre_dominant_emotion") or "joy").lower()
secondary = (book.get("secondary_emotion") or "").lower()


# ═══════════════════════════════════════
# HERO CARD
# ═══════════════════════════════════════

genres_html = ""
for g in genres:
    genres_html += f'<span style="display:inline-block; margin-right:6px; padding:6px 10px; border-radius:999px; background:#0F172A; color:#94A3B8; font-size:12px;">{g}</span>'

dom_info = EMOTION_COLORS.get(dominant, EMOTION_COLORS["joy"])
sec_info = EMOTION_COLORS.get(secondary, {}) if secondary else None

viral_label = book.get("viral_label") or book.get("viral_label_text") or book.get("viral_label", "")
viral_color = "#10B981" if viral_label and "high" in viral_label.lower() else ("#F59E0B" if viral_label and "moderate" in viral_label.lower() else "#94A3B8")

raw_stats = (
    f'⭐ {book.get("rating","N/A")}'
    f' &nbsp;&nbsp; 📊 {book.get("rating_count","-")}'
    f' &nbsp;&nbsp; 💬 {book.get("review_count","-")}'
    f' &nbsp;&nbsp; 📚 {book.get("want_to_read_count","-")}'
    f' &nbsp;&nbsp; 📖 {book.get("page_count","-")}'
    f' &nbsp;&nbsp; 💰 {book.get("price","-")}'
)

top_standout = book.get("top_genre_standout_score") or ""
top_standout_display = top_standout
if top_standout:
    parts = top_standout.split(":", 2)
    if len(parts) == 2:
        standout_genre = parts[0].strip()
        try:
            standout_score = float(parts[1])
        except Exception:
            standout_score = None
        if standout_score is not None:
            delta_pct = (standout_score - 1.0) * 100
            if abs(delta_pct) < 0.05:
                top_standout_display = f"{standout_genre} · about average"
            elif delta_pct > 0:
                top_standout_display = f"{standout_genre} · {delta_pct:.0f}% above average"
            else:
                top_standout_display = f"{standout_genre} · {abs(delta_pct):.0f}% below average"

# Prepare variables for hero card (image, emotion badges, viral styling)
book_doc = book
viral_doc = book
emotion_doc = book

dominant_key = (emotion_doc.get("dominant_emotion") or "joy").lower()
secondary_key = (emotion_doc.get("secondary_emotion") or "").lower()
dominant_info = EMOTION_COLORS.get(dominant_key, EMOTION_COLORS["joy"])
secondary_info = EMOTION_COLORS.get(secondary_key, EMOTION_COLORS["joy"]) if secondary_key else None
dominant_color = dominant_info.get("color")
dominant_emoji = dominant_info.get("icon")
secondary_color = secondary_info.get("color") if secondary_info else "#94A3B8"
secondary_emoji = secondary_info.get("icon") if secondary_info else ""

viral_label = viral_doc.get("viral_label") or viral_doc.get("viral_label_text") or ""
if viral_label and "high" in viral_label.lower():
        viral_bg = "#10B98122"
        viral_text = "#10B981"
        viral_border = "#10B98144"
        viral_icon = "🔥"
elif viral_label and "moderate" in viral_label.lower():
        viral_bg = "#F59E0B22"
        viral_text = "#F59E0B"
        viral_border = "#F59E0B44"
        viral_icon = "⚡"
else:
        viral_bg = "#64748B22"
        viral_text = "#64748B"
        viral_border = "#64748B44"
        viral_icon = "💤"

# Image URL fallback
image_url = book_doc.get("image_url") or book_doc.get("cover_url") or book_doc.get("thumbnail") or book_doc.get("image") or ""
if not image_url:
        import urllib.parse
        title_encoded = urllib.parse.quote(book_doc.get("title", ""))
        image_url = f"https://covers.openlibrary.org/b/title/{title_encoded}-M.jpg"

# HERO CARD — REBUILT WITH STREAMLIT LAYOUT
hero_left, hero_right = st.columns([1, 5], gap="large")

with hero_left:
    if not image_url:
        import urllib.parse
        title_encoded = urllib.parse.quote(book_doc.get("title", ""))
        image_url = f"https://covers.openlibrary.org/b/title/{title_encoded}-M.jpg"
    try:
        st.image(image_url, use_container_width=True)
    except Exception:
        st.markdown(
            "<div style=\"width:180px; height:270px; background:linear-gradient(135deg,#4F46E5,#7C3AED); "
            "border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:48px;\">📖</div>",
            unsafe_allow_html=True,
        )

with hero_right:
    st.markdown(f"## {book_doc.get('title', 'Unknown Title')}")
    st.caption(f"{book_doc.get('author', 'Unknown Author')}{' · Published: ' + publish if publish else ''}")

    genres = book_doc.get("genres", [])
    if isinstance(genres, list) and len(genres) > 0:
        genre_pills = " ".join(
            f"<span style=\"background:#334155; color:#CBD5E1; padding:4px 12px; border-radius:999px; "
            f"font-size:12px; font-weight:600; display:inline-block; margin-right:4px; margin-bottom:4px;\">{g}</span>"
            for g in genres[:5]
        )
        st.markdown(genre_pills, unsafe_allow_html=True)

    badges_html = ""
    badges_html += (
        f"<span style=\"background:{dominant_color}22; color:{dominant_color}; padding:5px 14px; border-radius:999px; "
        f"font-size:12px; font-weight:700; border:1px solid {dominant_color}44; display:inline-block; margin-right:6px;\">"
        f"{dominant_emoji} {dominant_key.capitalize()} (Dominant)</span>"
    )
    if secondary_key:
        badges_html += (
            f"<span style=\"background:{secondary_color}22; color:{secondary_color}; padding:5px 14px; border-radius:999px; "
            f"font-size:12px; font-weight:700; border:1px solid {secondary_color}44; display:inline-block; margin-right:6px;\">"
            f"{secondary_emoji} {secondary_key.capitalize()}</span>"
        )
    badges_html += (
        f"<span style=\"background:{viral_bg}; color:{viral_text}; padding:5px 14px; border-radius:999px; "
        f"font-size:12px; font-weight:700; border:1px solid {viral_border}; display:inline-block;\">{viral_icon} {viral_label}</span>"
    )
    st.markdown(badges_html, unsafe_allow_html=True)

    stats_html = (
        "<div style=\"display:flex; flex-wrap:wrap; gap:20px; font-size:12px; "
        "font-family:ui-monospace,monospace; margin-top:12px;\">"
        f"<span style=\"color:{text_muted};\">⭐ Rating: <span style=\"color:{text_value}; font-weight:600;\">{book_doc.get('rating', 'N/A')}</span></span>"
        f"<span style=\"color:{text_muted};\">📊 Ratings: <span style=\"color:{text_value}; font-weight:600;\">{format_count(book_doc.get('rating_count', 0))}</span></span>"
        f"<span style=\"color:{text_muted};\">💬 Reviews: <span style=\"color:{text_value}; font-weight:600;\">{format_count(book_doc.get('review_count', 0))}</span></span>"
        f"<span style=\"color:{text_muted};\">📚 Want to Read: <span style=\"color:{text_value}; font-weight:600;\">{format_count(book_doc.get('want_to_read_count', 0))}</span></span>"
        f"<span style=\"color:{text_muted};\">📖 Pages: <span style=\"color:{text_value}; font-weight:600;\">{book_doc.get('page_count', 'N/A')}</span></span>"
        f"<span style=\"color:{text_muted};\">💰 Price: <span style=\"color:{text_value}; font-weight:600;\">{book_doc.get('price', 'N/A')}</span></span>"
        "</div>"
    )
    st.markdown(stats_html, unsafe_allow_html=True)

    if top_standout_display:
        st.markdown(
            f"<div style=\"margin-top:12px; margin-bottom:24px;\"><span style=\"background:#4F46E522; color:#A5B4FC; padding:6px 14px; "
            f"border-radius:8px; font-size:13px; font-weight:700; border:1px solid #4F46E544; display:inline-block;\">"
            f"🏆 {top_standout_display}</span></div>",
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════
# KPI ROW
# ═══════════════════════════════════════

k1, k2, k3, k4 = st.columns(4)
true_sat = book.get("true_satisfaction", 0)
eng_depth = book.get("engagement_depth_score", 0)
viral_score = book.get("viral_potential_score", 0)
bfb = book.get("normalized_bang_for_buck", 0)

def metric_col(col, label, value):
    col.markdown(f"<div style='color:{text_muted}; font-size:12px; font-weight:700;'>{label}</div>", unsafe_allow_html=True)
    col.markdown(f"<div style='font-family:ui-monospace,monospace; font-size:20px; font-weight:800; color:{text_primary};'>{fmt_percent(value)}</div>", unsafe_allow_html=True)
    try:
        col.progress(float(value))
    except Exception:
        col.progress(0.0)

metric_col(k1, "True Satisfaction", true_sat)
metric_col(k2, "Engagement Depth", eng_depth)
metric_col(k3, "Viral Potential", viral_score)
metric_col(k4, "Bang for Buck", bfb)

st.markdown("---")


# ═══════════════════════════════════════
# Tabs: Detailed Metrics
# ═══════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Sentiment & Opinion", "🧠 Emotion Profile", "📊 Engagement & Quality", "🚀 Virality & Standout"])

with tab1:

    # Top row
    top_left, top_right = st.columns(2, gap="large")

    with top_left:
        st.markdown("**Avg Sentiment Score**")
        st.caption("The Positivity Metric")
        sentiment_val = book.get("avg_sentiment_score", 0)
        st.markdown(f"<p style='font-family:ui-monospace,monospace; font-size:32px; font-weight:700; margin:16px 0 8px 0;'>{sentiment_val:+.2f}</p>", unsafe_allow_html=True)

        # Gradient spectrum bar with marker
        marker_pct = ((sentiment_val + 1) / 2) * 100
        render_html(f"""
        <div style="position:relative; margin:8px 0;">
            <div style="height:10px; border-radius:999px; background:linear-gradient(to right, #EF4444, #94A3B8, #10B981);"></div>
            <div style="position:absolute; top:50%; left:{marker_pct}%; transform:translate(-50%,-50%); width:16px; height:16px; background:white; border:3px solid #4F46E5; border-radius:50%; box-shadow:0 2px 6px rgba(0,0,0,0.3);"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:10px; font-weight:700; color:#94A3B8; margin-top:4px;">
            <span>Negative</span><span>Neutral</span><span>Positive</span>
        </div>
        """)

    with top_right:
        st.markdown("**Sentiment Strength**")
        st.caption("The Intensity Metric")
        strength_val = book.get("sentiment_strength", 0)
        st.markdown(f"<p style='font-family:ui-monospace,monospace; font-size:32px; font-weight:700; margin:16px 0 8px 0;'>{fmt_percent(strength_val)}</p>", unsafe_allow_html=True)
        try:
            st.progress(min(max(float(strength_val), 0.0), 1.0))
        except Exception:
            st.progress(0.0)
        left_l, right_l = st.columns(2)
        left_l.caption("Apathetic")
        right_l.markdown(f"<p style='text-align:right; font-size:12px; color:{text_muted};'>Polarizing</p>", unsafe_allow_html=True)

    # Spacer
    st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

    # Bottom row
    bot_left, bot_right = st.columns(2, gap="large")

    with bot_left:
        st.markdown("**Normalized Sentiment Strength**")
        st.caption("Standardized 0–1 scale relative to database")
        norm_strength = book.get("normalized_sentiment_strength", 0)
        st.markdown(f"<p style='font-family:ui-monospace,monospace; font-size:32px; font-weight:700; margin:16px 0 8px 0;'>{fmt_percent(norm_strength)}</p>", unsafe_allow_html=True)
        try:
            st.progress(min(max(float(norm_strength), 0.0), 1.0))
        except Exception:
            st.progress(0.0)

    with bot_right:
        st.markdown("**Review Conversion**")
        st.caption("The Compulsion Metric — rate of readers who write reviews")
        conversion = book.get("normalized_review_conversion", 0)
        st.markdown(f"<p style='font-family:ui-monospace,monospace; font-size:32px; font-weight:700; margin:16px 0 8px 0;'>{fmt_percent(conversion)}</p>", unsafe_allow_html=True)
        try:
            st.progress(min(max(float(conversion), 0.0), 1.0))
        except Exception:
            st.progress(0.0)

with tab2:
    left, right = st.columns([6,4])
    # Emotion bars (single HTML block)
    emo_items = [
        ("joy", book.get("emotion_joy", book.get("emotion_joy", 0))),
        ("anger", book.get("emotion_anger", 0)),
        ("sadness", book.get("emotion_sadness", 0)),
        ("fear", book.get("emotion_fear", 0)),
        ("surprise", book.get("emotion_surprise", 0)),
    ]
    # sort by value desc
    emo_items = sorted(emo_items, key=lambda x: x[1], reverse=True)

    bars_html = ""
    for idx, (ename, val) in enumerate(emo_items):
        info = EMOTION_COLORS.get(ename, EMOTION_COLORS["joy"])
        badge = ""
        if idx == 0:
            badge = f'<span style="font-size:9px; font-weight:700; padding:2px 8px; border-radius:999px; background:{info["bg"]}; color:{info["color"]}; margin-left:6px;">PRIMARY</span>'
        elif idx == 1:
            badge = f'<span style="font-size:9px; font-weight:700; padding:2px 8px; border-radius:999px; background:{info["bg"]}; color:{info["color"]}; margin-left:6px;">SECONDARY</span>'
        try:
            pct = max(0, min(100, float(val) * 100))
        except Exception:
            pct = 0
        bars_html += (
            f'<div style="margin-bottom:12px;">'
            f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">'
            f'<span style="font-size:13px; font-weight:600;">{info["icon"]} {ename.capitalize()}{badge}</span>'
            f'<span style="font-family:ui-monospace,monospace; font-weight:700; color:{info["color"]};">{val:.2f}</span>'
            f'</div>'
            f'<div style="width:100%; height:12px; border-radius:999px; overflow:hidden; background:{info["bg"]};">'
            f'<div style="height:100%; width:{pct}%; border-radius:999px; background:{info["color"]};"></div>'
            f'</div>'
            f'</div>'
        )
    left.markdown(bars_html, unsafe_allow_html=True)

    # Right summary card
    dom = emo_items[0][0]
    dom_info = EMOTION_COLORS.get(dom, EMOTION_COLORS["joy"])
    sec = emo_items[1][0] if len(emo_items) > 1 else ""
    complexity = book.get("emotional_complexity_score", 0)
    avg_emotion = book.get("avg_emotion_intensity", book.get("avg_review_emotion", 0))

    right.markdown(
        f'<div style="background:#0F172A; border-radius:12px; padding:20px; min-height:240px;">'
        f'<div style="font-size:28px; margin-bottom:12px;">{dom_info["icon"]}</div>'
        f'<div style="display:inline-block; padding:6px 10px; border-radius:999px; background:{dom_info["color"]}; color:white; font-weight:700;">Dominant Emotion</div>'
        f'<h2 style="color:white; margin-top:8px;">{dom.capitalize()}</h2>'
        f'<div style="color:#94A3B8; margin-top:8px;">Secondary: {EMOTION_COLORS.get(sec, {}).get("icon"," ")} {sec.capitalize() if sec else "N/A"}</div>'
        f'<div style="margin-top:12px; font-weight:700;">Emotional Complexity: {fmt(complexity)}</div>'
        f'<div style="margin-top:6px;">'
        f'<div style="height:10px; border-radius:999px; background:#0B1220; margin-top:6px;">'
        f'<div style="height:100%; width:{max(0,min(100, complexity*100))}%; background:#6366F1; border-radius:999px;"></div>'
        f'</div>'
        f'<div style="color:#94A3B8; margin-top:6px;">One Mood — Rollercoaster</div>'
        f'</div>'
        f'<div style="margin-top:8px; color:#94A3B8;">Avg Emotion Intensity: {fmt(avg_emotion)}</div>'
        f'</div>', unsafe_allow_html=True)

with tab3:
    cols = st.columns(3)
    norm_rating = book.get("normalized_rating", 0)
    reviewer_eng = book.get("reviewer_engagement_score", 0)
    eng_depth = book.get("engagement_depth_score", 0)
    
    cols[0].metric(
        "Relative Rating Score",
        fmt_percent(norm_rating),
        help="A score that shows how this book's rating compares to others in the dataset. Higher values mean the book is rated closer to the highest-rated books in the system.",
    )
    try:
        cols[0].progress(min(max(float(norm_rating), 0.0), 1.0))
    except Exception:
        cols[0].progress(0.0)

    cols[1].metric(
        "Review Detail Level",
        fmt_percent(reviewer_eng),
        help="Shows how detailed and thoughtful reader reviews are, based on review length and depth. Higher values indicate more engaged and expressive reviewers.",
    )
    try:
        cols[1].progress(min(max(float(reviewer_eng), 0.0), 1.0))
    except Exception:
        cols[1].progress(0.0)

    cols[2].metric(
        "Reader Engagement Level",
        fmt_percent(eng_depth),
        help="Measures overall reader interaction with the book, including reading activity and review participation. Higher values indicate stronger audience involvement.",
    )
    try:
        cols[2].progress(min(max(float(eng_depth), 0.0), 1.0))
    except Exception:
        cols[2].progress(0.0)

    bcols = st.columns(3)
    ts = book.get("true_satisfaction", 0)
    nt = book.get("normalized_timelessness", 0)
    bf = book.get("normalized_bang_for_buck", 0)
    
    bcols[0].metric(
        "Reader Satisfaction Score",
        fmt_percent(ts),
        help="Combines reader ratings with engagement levels to reflect how satisfied and emotionally connected readers are with the book. Higher values indicate stronger overall satisfaction.",
    )
    try:
        bcols[0].progress(min(max(float(ts), 0.0), 1.0))
    except Exception:
        bcols[0].progress(0.0)

    bcols[1].metric(
        "Long-Term Popularity",
        fmt_percent(nt),
        help="Indicates how well the book maintains interest over time. Higher values mean the book continues to stay relevant and widely appreciated.",
    )
    try:
        bcols[1].progress(min(max(float(nt), 0.0), 1.0))
    except Exception:
        bcols[1].progress(0.0)

    bcols[2].metric(
        "Value for Money",
        fmt_percent(bf),
        help="Represents how much value readers feel they get from the book compared to its effort, time, or cost. Higher values indicate better perceived value.",
    )
    try:
        bcols[2].progress(min(max(float(bf), 0.0), 1.0))
    except Exception:
        bcols[2].progress(0.0)

with tab4:
    # Viral hero
    vp = book.get("viral_potential_score", 0)
    vlabel = book.get("viral_label", "")
    st.markdown(f"<div style='display:flex; align-items:center; gap:12px;'><div style='font-size:36px; font-weight:800;'>{fmt(vp)}</div><div style='padding:6px 10px; border-radius:999px; background:{viral_color}; color:white; font-weight:700;'>{vlabel}</div></div>", unsafe_allow_html=True)

    # Breakdown bars (single HTML block)
    components = [
        ("Engagement Depth", 0.35, book.get("engagement_depth_score",0)),
        ("Review Conversion", 0.25, book.get("normalized_review_conversion",0)),
        ("Demand Pressure", 0.20, book.get("normalized_demand_pressure",0)),
        ("Sentiment Strength", 0.15, book.get("normalized_sentiment_strength", book.get("sentiment_strength",0))),
        ("Emotion Intensity", 0.05, book.get("avg_emotion_intensity", book.get("avg_review_emotion",0)))
    ]
    breakdown_html = ""
    for name, weight, val in components:
        try:
            pct = max(0, min(100, float(val) * 100))
        except Exception:
            pct = 0
        if pct >= 67:
            bar_color = "#10B981"
        elif pct >= 34:
            bar_color = "#F59E0B"
        else:
            bar_color = "#94A3B8"
        breakdown_html += (
            f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">'
            f'<div style="width:30%; color:#94A3B8;">{name} ({int(weight*100)}%)</div>'
            f'<div style="width:65%; background:#0B1220; border-radius:999px; overflow:hidden;">'
            f'<div style="height:12px; width:{pct}%; background:{bar_color};"></div>'
            f'</div>'
            f'<div style="width:5%; text-align:right; font-family:ui-monospace,monospace;">{pct:.0f}%</div>'
            f'</div>'
        )
    st.markdown(breakdown_html, unsafe_allow_html=True)

    st.markdown("### Genre Standout Performance")
    standout = book.get("standout_scores", []) or []
    # Bars (single block)
    shtml = ""
    for item in standout:
        g = item.get("genre")
        score = item.get("standout_score", 0)
        color = "#10B981" if score > 1.0 else ("#94A3B8" if abs(score-1.0) < 1e-6 else "#EF4444")
        width = max(0, min(100, (score / 2) * 100))  # normalize to 0-2 scale
        if score > 1.0:
            tag_text = "Above avg"
        elif abs(score - 1.0) < 1e-6:
            tag_text = "At avg"
        else:
            tag_text = "Below avg"
        star = " ⭐" if f"{g}:" in (book.get("top_genre_standout_score") or "") else ""
        shtml += (
            f'<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">'
            f'<div style="width:220px; color:#94A3B8;">{g}</div>'
            f'<div style="flex:1; background:#0B1220; border-radius:999px; overflow:hidden;">'
            f'<div style="height:12px; width:{width}%; background:{color};"></div>'
            f'</div>'
            f'<div style="width:150px; text-align:right; font-family:ui-monospace,monospace;">'
            f'<span style="display:inline-block; margin-right:6px; padding:2px 6px; border-radius:999px; background:{color}22; color:{color}; font-size:10px; font-weight:700;">{tag_text}</span>'
            f'{score:.2f}{star}</div>'
            f'</div>'
        )
    st.markdown(shtml, unsafe_allow_html=True)


