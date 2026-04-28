import pandas as pd
import numpy as np
from pymongo import MongoClient, UpdateOne

client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
collection1 = db["book_emotion_summary"]
collection2 = db["books"]

cursor1 = collection1.find({}, {"_id": 0, "book_id": 1, "normalized_sentiment_strength": 1 })
cursor2 = collection2.find({}, {"_id": 0, "book_id": 1, "normalized_review_conversion": 1,"avg_review_emotion": 1, "reviewer_engagement_score": 1})

df1 = pd.DataFrame(list(cursor1))
df2 = pd.DataFrame(list(cursor2))
df3 = pd.merge(df1, df2, on='book_id', how='inner')

# Calculate Engagement Depth Score (Weighted Average)
df3["engagement_depth_score"] = (df3['normalized_sentiment_strength'] * 0.2 + df3['normalized_review_conversion'] * 0.2 + df3['avg_review_emotion'] * 0.3 + df3['reviewer_engagement_score'] * 0.3) 


updates = []
for row in df3.itertuples(index=False):
    updates.append(
        UpdateOne(
            {"book_id": row.book_id},
            {"$set": {
                "engagement_depth_score": row.engagement_depth_score
            }}
        )
    )

if updates:
    result = collection2.bulk_write(updates)
    print(f"Successfully updated {result.modified_count} books with engagement depth scores.")