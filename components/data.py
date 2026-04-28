import streamlit as st
import pandas as pd
from components.database import get_database


@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_all_genres():
    """Fetch all genre analysis documents."""
    db = get_database()
    cursor = db["genre_analysis"].find({}, {"_id": 0})
    return pd.DataFrame(list(cursor))


@st.cache_data(ttl=600)
def get_genre_by_name(genre_name: str):
    """Fetch a single genre document by name."""
    db = get_database()
    return db["genre_analysis"].find_one(
        {"genres": genre_name},
        {"_id": 0}
    )


@st.cache_data(ttl=600)
def get_genre_names():
    """Fetch just the genre names for the dropdown."""
    db = get_database()
    docs = db["genre_analysis"].find(
        {},
        {"_id": 0, "genres": 1}
    ).sort("total_books", -1)
    return [doc["genres"] for doc in docs]


@st.cache_data(ttl=600)
def get_all_books():
    """Fetch all books with their computed metrics."""
    db = get_database()
    cursor = db["books"].find({}, {
        "_id": 0,
        "title": 1,
        "genres": 1,
        "true_satisfaction": 1,
        "engagement_depth_score": 1,
        "normalized_rating": 1,
        "emotional_complexity_score": 1,
        "normalized_bang_for_buck": 1,
        "normalized_timelessness": 1,
        "standout_scores": 1,
        "top_genre_standout_score": 1,
        "sentiment_strength": 1,
        "avg_review_emotion": 1,
    })
    return pd.DataFrame(list(cursor))


@st.cache_data(ttl=600)
def get_books_by_genre(genre_name: str):
    """Fetch books belonging to a specific genre."""
    db = get_database()
    cursor = db["books"].find(
        {"genres": genre_name},
        {"_id": 0}
    )
    return pd.DataFrame(list(cursor))