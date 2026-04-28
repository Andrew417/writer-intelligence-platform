import pandas as pd
import numpy as np
from pymongo import MongoClient, UpdateOne

client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
collection = db["books"]

cursor = collection.find({}, {"_id": 0, "book_id": 1, "review_count": 1, "rating_count": 1})

df = pd.DataFrame(list(cursor))

# Drop any rows where review_count or rating_count is missing
df = df.dropna(subset=['review_count', 'rating_count'])

# Convert rating_count and review_count to integers (remove commas if present)
df['rating_count'] = df['rating_count'].str.replace(',', '').astype(int)
df['review_count'] = df['review_count'].str.replace(',', '').astype(int)

# Calculate review conversion rate
df['review_conversion_rate'] = df['review_count'] / df['rating_count']

# Find global min and max of these averages
min_val = df['review_conversion_rate'].min()
max_val = df['review_conversion_rate'].max()
print(f"Min: {min_val}, Max: {max_val}")

# Normalize the review conversion rate to a 0-1 scale
df['normalized_review_conversion'] = (df['review_conversion_rate'] - min_val) / (max_val - min_val)

# Prepare bulk updates for MongoDB
updates = []
for row in df.itertuples(index=False):
    updates.append(
        UpdateOne(
            {"book_id": row.book_id},
            {"$set": {
                "normalized_review_conversion": row.normalized_review_conversion,
                "rating_count": row.rating_count,  # This updates the DB field to an integer
                "review_count": row.review_count   # This updates the DB field to an integer
            }}
        )
    )

# Execute the bulk write
if updates:
    result = collection.bulk_write(updates)
    print(f"Successfully updated {result.modified_count} books with normalized review conversion rates.")