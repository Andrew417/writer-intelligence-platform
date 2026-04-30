import streamlit as st
import pandas as pd
from components.database import get_database


# ─────────────────────────────────────────────────────────────
#  GENRES
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_all_genres():
    """
    Full genre analysis — superset of fields needed by both Dashboard and Marketplace.
    - Marketplace uses: genres, market_risk_index
    - Dashboard uses:   genres, total_books, avg_* metrics, etc.
    """
    db = get_database()
    cursor = db["genre_analysis"].find({}, {
        "_id": 0,
        "genres": 1,
        "total_books": 1,
        "genre_dominant_emotion": 1,
        "market_risk_index": 1,
        "avg_joy": 1,
        "avg_sadness": 1,
        "avg_anger": 1,
        "avg_fear": 1,
        "avg_surprise": 1,
        "avg_satisfaction": 1,
        "avg_engagement_depth": 1,
        "avg_emotional_complexity": 1,
        "avg_sentiment_strength": 1,
        "avg_bang_for_buck": 1,
        "avg_viral_potential": 1,
        "avg_timelessness": 1,
        "avg_sentiment": 1
    })
    return pd.DataFrame(list(cursor))


@st.cache_data(ttl=600)
def get_genre_by_name(genre_name: str):
    db = get_database()
    return db["genre_analysis"].find_one({"genres": genre_name}, {"_id": 0})


@st.cache_data(ttl=600)
def get_genre_names():
    db = get_database()
    docs = db["genre_analysis"].find({}, {"_id": 0, "genres": 1}).sort("total_books", -1)
    return [doc["genres"] for doc in docs]


# ─────────────────────────────────────────────────────────────
#  BOOKS
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_all_books():
    """
    Books with ALL flags.
    - Dashboard uses:   hidden_gem_flag, viral_potential_score, true_satisfaction, etc.
    - Marketplace uses: hidden_gem_flag + viral_breakout_flag (extra)
    """
    db = get_database()
    cursor = db["books"].find({}, {
        "_id": 0,
        "book_id": 1,
        "title": 1,
        "author": 1,
        "genres": 1,
        "scraped_reviews_count": 1,
        "rating_count": 1,
        "true_satisfaction": 1,
        "viral_potential_score": 1,
        "normalized_bang_for_buck": 1,
        "days_since_published": 1,
        "clean_price": 1,
        "price": 1,
        "engagement_depth_score": 1,
        "hidden_gem_flag": 1,
        "viral_breakout_flag": 1     # ← needed by Marketplace
    })
    return pd.DataFrame(list(cursor))


@st.cache_data(ttl=600)
def get_books_by_genre(genre_name: str):
    db = get_database()
    cursor = db["books"].find({"genres": genre_name}, {"_id": 0})
    return pd.DataFrame(list(cursor))


# ─────────────────────────────────────────────────────────────
#  EMOTIONS
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_book_emotions():
    db = get_database()
    cursor = db["book_emotion_summary"].find({}, {
        "_id": 0,
        "book_id": 1,
        "secondary_emotion": 1
    })
    return pd.DataFrame(list(cursor))


# ─────────────────────────────────────────────────────────────
#  REVIEWS
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_total_reviews_count():
    """Used by Dashboard. Counts NLP-analyzed reviews."""
    db = get_database()
    return db["review_nlp_analysis"].count_documents({})


# ─────────────────────────────────────────────────────────────
#  MARKET TRENDS  (both screens need this collection)
# ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=600)
def get_market_trends():
    """
    Used by Marketplace.
    Fetches the FULL pre-calculated market_trends collection
    (pricing brackets, global mood, etc.).
    """
    db = get_database()
    cursor = db["market_trends"].find({}, {"_id": 0})
    return pd.DataFrame(list(cursor))


@st.cache_data(ttl=600)
def get_global_market_mood():
    """
    Used by Dashboard.
    Fetches ONLY the global market mood document for the header badge.
    """
    db = get_database()
    doc = db["market_trends"].find_one(
        {"trend_type": "global_market_mood"},
        {"_id": 0}
    )
    return doc if doc else {}
