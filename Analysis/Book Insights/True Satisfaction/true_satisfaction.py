import pandas as pd
import numpy as np
from pymongo import MongoClient, UpdateOne

client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
collection = db["books"]

cursor = collection.find({}, {"_id": 0, "book_id": 1, "normalized_rating": 1,"engagement_depth_score": 1})

df = pd.DataFrame(list(cursor))

# Calculate true satisfaction score as a weighted average of normalized rating and engagement depth score
# why use both? because they both contribute to the overall satisfaction of the user.
# Normalized rating reflects the user's overall satisfaction with the book,
# while engagement depth score reflects how deeply the user engaged with the book.
# By combining both, we can get a more comprehensive measure of true satisfaction.
df["true_satisfaction"] = df["normalized_rating"] * 0.5 + df["engagement_depth_score"] * 0.5

# Save it back to the database
updates = []
for row in df.itertuples(index=False):
    updates.append(
        UpdateOne(
            {"book_id": row.book_id},
            {"$set": {
                "true_satisfaction": row.true_satisfaction
            }}
        )
    )

if updates:
    result = collection.bulk_write(updates)
    print(f"Successfully updated {result.modified_count} books with true satisfaction scores.")

 