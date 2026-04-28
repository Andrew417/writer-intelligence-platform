import pandas as pd
import numpy as np
from pymongo import MongoClient, UpdateOne

# 1. Connect to MongoDB
client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
collection = db["reviews"]

# 2. Fetch data from MongoDB
cursor = collection.find({"in_nlp": True}, {"_id": 0, "book_id": 1, "review_text": 1})

# 3. Load directly into a Pandas DataFrame!
df = pd.DataFrame(list(cursor))

# Drop any rows where review_text is missing
df = df.dropna(subset=['review_text'])
print(df.info())

# 4. Use Vectorized Pandas/NumPy to do the math instantly (No 'for' loops!)
# Count words in every review at once
df['word_count'] = df['review_text'].str.split().str.len()

# Group by book_id to get the average word count per book
book_stats = df.groupby('book_id')['word_count'].mean().reset_index()
book_stats.rename(columns={'word_count': 'avg_word_count'}, inplace=True)

# 5. Math & Normalization using NumPy
# Find global min and max of these averages
min_expected = book_stats['avg_word_count'].min()
max_expected = book_stats['avg_word_count'].max()

# Log transform everything at once
book_stats['log_avg'] = np.log1p(book_stats['avg_word_count'])
log_min = np.log1p(min_expected)
log_max = np.log1p(max_expected)

# Calculate Reviewer Engagement (Normalized 0 to 1)
if log_max > log_min:
    book_stats['normalized_avg_review_length'] = (book_stats['log_avg'] - log_min) / (log_max - log_min)
else:
    book_stats['normalized_avg_review_length'] = 0

# now to update the MongoDB collection with these new scores, we can do a bulk update
bulk_updates = []
for row in book_stats.itertuples(index=False):
    bulk_updates.append(
        UpdateOne(
            {"book_id": row.book_id},  # Notice we use dot notation instead of brackets
            {"$set": {"reviewer_engagement_score": row.normalized_avg_review_length}}
        )
    )

if bulk_updates:
    result = db["books"].bulk_write(bulk_updates) 
    print(f"Updated {result.modified_count} books with reviewer engagement scores.")