import pandas as pd
import numpy as np
from pymongo import MongoClient, UpdateOne

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
books = db["books"]
book_emotion_summary = db["book_emotion_summary"]
market_trends = db["market_trends"]

book_cursor = books.find({}, {"_id": 0, "book_id": 1 ,"days_since_published": 1, "avg_review_emotion": 1, })

book_emotion_summary_cursor = book_emotion_summary.find({}, {"_id": 0, "book_id": 1 , "dominant_emotion": 1, "secondary_emotion": 1 })

book_df = pd.DataFrame(list(book_cursor))

book_emotion_summary_df = pd.DataFrame(list(book_emotion_summary_cursor))

# Merge the book dataframe with the book emotion summary dataframe on book_id
merged_df = pd.merge(book_df, book_emotion_summary_df, on='book_id', how='inner')

# filter days_since_published to be less than 1260
LOOKBACK_DAYS = 1260
merged_df = merged_df[merged_df['days_since_published'] < LOOKBACK_DAYS]

# Calculate the average of avg_review_emotion across all books in the merged dataframe
avg_review_emotion_mean = merged_df['avg_review_emotion'].mean()

# Determine the market mood based on the dominant emotion of the majority of books in the merged dataframe
# we used secondary emotion instead of dominant emotion because dominant emotion is mostly joy
market_mood = merged_df['secondary_emotion'].mode().iloc[0]

# save this to the market_trends collection in MongoDB with the following structure:
result = market_trends.update_one(
    {"trend_type": "global_market_mood"},  # This ID ensures we overwrite the old one instead of duplicating
    {"$set": {
        "lookback_days": LOOKBACK_DAYS,
        "avg_review_emotion_mean": avg_review_emotion_mean,
        "market_mood": market_mood,
        "books_analyzed": len(merged_df)
    }},
    upsert=True
)
print(f"Market mood updated with avg_review_emotion_mean: {avg_review_emotion_mean}, market_mood: {market_mood}, books_analyzed: {len(merged_df)}")

