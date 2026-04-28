import pandas as pd
import numpy as np
from pymongo import MongoClient, UpdateOne

client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
collection1 = db["book_emotion_summary"]
collection2 = db["books"]

cursor = collection1.find({}, {"_id": 0, "book_id": 1, "emotion_joy": 1, "emotion_anger": 1,
                                "emotion_sadness": 1, "emotion_fear": 1, "emotion_surprise": 1 })

df = pd.DataFrame(list(cursor))

emotions_std = df[['emotion_joy', 'emotion_anger', 'emotion_sadness', 'emotion_fear', 'emotion_surprise']].std(axis=1)

# Find min and max of the standard deviation
min_std = emotions_std.min()
max_std = emotions_std.max()
print(f"Min Std Dev: {min_std}, Max Std Dev: {max_std}")

# Min-Max Normalization (scales it between 0.0 and 1.0)
df['normalized_emotion_deviation'] = (emotions_std - min_std) / (max_std - min_std)

# Emotional Complexity Score is 1 - normalized deviation (because lower deviation = more complex)
df['emotional_complexity_score'] = 1 - df['normalized_emotion_deviation']

print(df[['book_id', 'emotional_complexity_score']])

# Save it back to the database
updates = []
for row in df.itertuples(index=False):
    updates.append(
        UpdateOne(
            {"book_id": row.book_id},
            {"$set": {
                "emotional_complexity_score": row.emotional_complexity_score
            }}
        )
    )

if updates:
    result = collection2.bulk_write(updates)
    print(f"Successfully updated {result.modified_count} books with emotional complexity score.")

 