import pandas as pd
import numpy as np
from pymongo import MongoClient, UpdateOne

client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
collection = db["books"]

cursor = collection.find({}, {"_id": 0, "book_id": 1, "rating": 1})

df = pd.DataFrame(list(cursor))

df['clean_rating'] = pd.to_numeric(df['rating'], errors='coerce')

# Calculate min and max for normalization
min_rating = df['clean_rating'].min()
max_rating = df['clean_rating'].max()

# Apply Relative Min-Max Normalization
df['normalized_rating'] = (df['clean_rating'] - min_rating) / (max_rating - min_rating)

# Save it back to the database
updates = []
for row in df.itertuples(index=False):
    updates.append(
        UpdateOne(
            {"book_id": row.book_id},
            {"$set": {
                "normalized_rating": row.normalized_rating
            }}
        )
    )

if updates:
    result = collection.bulk_write(updates)
    print(f"Successfully updated {result.modified_count} books with normalized ratings.")

 