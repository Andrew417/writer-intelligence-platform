import streamlit as st
import pandas as pd
from components.database import get_database

@st.cache_data(ttl=600)
def get_all_genres():
    db = get_database()
    cursor = db["genre_analysis"].find({}, {
        "_id": 0,
        "genres": 1,
        "total_books": 1,
        "genre_dominant_emotion": 1,
        "avg_joy": 1,
        "avg_sadness": 1,
        "avg_anger": 1,
        "avg_fear": 1,
        "avg_surprise": 1
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

@st.cache_data(ttl=600)
def get_all_books():
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
        "engagement_depth_score": 1 
    })
    return pd.DataFrame(list(cursor))

@st.cache_data(ttl=600)
def get_books_by_genre(genre_name: str):
    db = get_database()
    cursor = db["books"].find({"genres": genre_name}, {"_id": 0})
    return pd.DataFrame(list(cursor))

@st.cache_data(ttl=600)
def get_book_emotions():
    db = get_database()
    cursor = db["book_emotion_summary"].find({}, {
        "_id": 0,
        "book_id": 1,
        "secondary_emotion": 1      
    })
    return pd.DataFrame(list(cursor))

@st.cache_data(ttl=600)
def get_total_reviews_count():
    db = get_database()
    return db["reviews"].count_documents({})