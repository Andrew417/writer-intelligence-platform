import pandas as pd
import numpy as np
from pymongo import MongoClient

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', '{:.3f}'.format) 

client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]

# 1. FETCH BOOKS & GENRES
books_cursor = db["books"].find({}, {
    "_id": 0, "book_id": 1, "genres": 1, "true_satisfaction": 1, 
    "engagement_depth_score": 1, "normalized_bang_for_buck": 1, 
    "emotional_complexity_score": 1, "normalized_timelessness": 1, 
    "viral_potential_score": 1
})
df_books = pd.DataFrame(list(books_cursor))

# 2. FETCH BOOK EMOTION SUMMARY
emotion_cursor = db["book_emotion_summary"].find({}, {
    "_id": 0, "book_id": 1, "avg_sentiment_score": 1, 
    "emotion_joy": 1, "emotion_anger": 1, "emotion_sadness": 1, 
    "emotion_fear": 1, "emotion_surprise": 1, 
    "dominant_emotion": 1, "normalized_sentiment_strength": 1
})
df_emotions = pd.DataFrame(list(emotion_cursor))

# 3. MERGE THE TWO DATAFRAMES
df = pd.merge(df_books, df_emotions, on='book_id', how='left')

# 4. EXPLODE THE GENRES
df = df.explode('genres')
df = df.dropna(subset=['genres'])
df['genres'] = df['genres'].astype(str).str.strip()

# Helper function to find the most common word (mode) for dominant_emotion
def get_mode(x):
    m = x.mode()
    return m.iloc[0] if not m.empty else None

# 5. THE MASTER AGGREGATION
genre_analysis = df.groupby('genres').agg(
    total_books=('book_id', 'count'),
    
    # Core Metrics
    avg_satisfaction=('true_satisfaction', 'mean'),
    avg_engagement_depth=('engagement_depth_score', 'mean'),
    avg_bang_for_buck=('normalized_bang_for_buck', 'mean'),
    avg_viral_potential=('viral_potential_score', 'mean'),
    avg_timelessness=('normalized_timelessness', 'mean'),
    avg_emotional_complexity=('emotional_complexity_score', 'mean'),
    
    # NLP Emotion Metrics
    avg_sentiment=('avg_sentiment_score', 'mean'),
    avg_sentiment_strength=('normalized_sentiment_strength', 'mean'),
    avg_joy=('emotion_joy', 'mean'),
    avg_anger=('emotion_anger', 'mean'),
    avg_sadness=('emotion_sadness', 'mean'),
    avg_fear=('emotion_fear', 'mean'),
    avg_surprise=('emotion_surprise', 'mean'),
    
    # Categorical Metric (Most frequent dominant emotion in this genre)
    genre_dominant_emotion=('dominant_emotion', get_mode)
).reset_index()

# Filter outliers (only keep genres with 5+ books)
genre_analysis = genre_analysis[genre_analysis['total_books'] >= 5]

# --- DISPLAY NEW NLP INSIGHTS ---
# Display the top 5 genres for each metric
print("\n🚀 TOP 5 GENRES: VIRAL POTENTIAL (Most likely to blow up on BookTok/Social Media)")
print(genre_analysis.sort_values('avg_viral_potential', ascending=False)[['genres', 'total_books', 'avg_viral_potential']].head(5))

print("\n🏆 TOP 5 GENRES: TRUE SATISFACTION (Most loved & defended by readers)")
print(genre_analysis.sort_values('avg_satisfaction', ascending=False)[['genres', 'total_books', 'avg_satisfaction']].head(5))

print("\n🔥 TOP 5 GENRES: ENGAGEMENT DEPTH (Most fiercely debated/discussed)")
print(genre_analysis.sort_values('avg_engagement_depth', ascending=False)[['genres', 'total_books', 'avg_engagement_depth']].head(5))

print("\n💰 TOP 5 GENRES: BANG FOR BUCK (Best value for the reader's money)")
print(genre_analysis.sort_values('avg_bang_for_buck', ascending=False)[['genres', 'total_books', 'avg_bang_for_buck']].head(5))

print("\n🎢 TOP 5 GENRES: EMOTIONAL COMPLEXITY (The biggest emotional rollercoasters)")
print(genre_analysis.sort_values('avg_emotional_complexity', ascending=False)[['genres', 'total_books', 'avg_emotional_complexity']].head(5))

print("\n🏛️ TOP 5 GENRES: TIMELESSNESS (The longest-lasting cultural impact)")
print(genre_analysis.sort_values('avg_timelessness', ascending=False)[['genres', 'total_books', 'avg_timelessness']].head(5))

print("\n😁 TOP 5 GENRES: MOST JOYFUL")
print(genre_analysis.sort_values('avg_joy', ascending=False)[['genres', 'total_books', 'avg_joy', 'genre_dominant_emotion']].head(5))

print("\n😱 TOP 5 GENRES: MOST FEAR/SUSPENSE")
print(genre_analysis.sort_values('avg_fear', ascending=False)[['genres', 'total_books', 'avg_fear', 'genre_dominant_emotion']].head(5))

print("\n🤬 TOP 5 GENRES: MOST ANGER/FRUSTRATION")
print(genre_analysis.sort_values('avg_anger', ascending=False)[['genres', 'total_books', 'avg_anger', 'genre_dominant_emotion']].head(5))

print("\n🧠 TOP 5 GENRES: OVERALL SENTIMENT STRENGTH (Most intense feelings overall)")
print(genre_analysis.sort_values('avg_sentiment_strength', ascending=False)[['genres', 'total_books', 'avg_sentiment_strength', 'genre_dominant_emotion']].head(5))

# --- CHECK FOR NaN VALUES ---
nan_rows = genre_analysis[genre_analysis.isna().any(axis=1)]
if not nan_rows.empty:
    print("\n⚠️ WARNING: Found genres with missing (NaN) values. They will be converted to nulls in MongoDB.")

# --- DATABASE INSERTION ---
# 1. Protect against MongoDB NaN crash
genre_analysis = genre_analysis.replace({np.nan: None})

# 2. Clear out the old analysis 
db["genre_analysis"].delete_many({})

# 3. Insert the fresh data
db["genre_analysis"].insert_many(genre_analysis.to_dict('records'))
print(f"\n✅ Successfully saved {len(genre_analysis)} genres with Full Emotion Profiles to MongoDB.")