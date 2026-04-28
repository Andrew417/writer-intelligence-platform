import pandas as pd
import numpy as np
from pymongo import MongoClient, UpdateOne

client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
collection = db["book_emotion_summary"]

cursor = collection.find({}, {"_id": 0, "book_id": 1, "avg_sentiment_score": 1 })

df = pd.DataFrame(list(cursor))

# Drop any rows where avg_sentiment_score is missing
df = df.dropna(subset=['avg_sentiment_score'])

# Calculate the absolute value of the average sentiment score to get the strength
df['sentiment_strength'] = df['avg_sentiment_score'].abs()

# Find min and max of the strength
min_strength = df['sentiment_strength'].min()
max_strength = df['sentiment_strength'].max()
print(f"Min Strength: {min_strength}, Max Strength: {max_strength}")

# Min-Max Normalization (scales it between 0.0 and 1.0)
df['normalized_sentiment_strength'] = (df['sentiment_strength'] - min_strength) / (max_strength - min_strength)

# Save it back to the database
updates = []
for row in df.itertuples(index=False):
    updates.append(
        UpdateOne(
            {"book_id": row.book_id},
            {"$set": {
                "sentiment_strength": row.sentiment_strength,
                "normalized_sentiment_strength": row.normalized_sentiment_strength
            }}
        )
    )

if updates:
    result = collection.bulk_write(updates)
    print(f"Successfully updated {result.modified_count} books with sentiment strength and normalized sentiment strength.")