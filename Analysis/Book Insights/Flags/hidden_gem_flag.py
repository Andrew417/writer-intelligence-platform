import pandas as pd
import numpy as np
from pymongo import MongoClient, UpdateOne

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
books = db["books"]
genre_analysis = db["genre_analysis "]

book_cursor = books.find({}, {"_id": 0, "book_id": 1,"true_satisfaction":1,"rating_count": 1})

book_df = pd.DataFrame(list(book_cursor))

# Calculate the hidden gem flag for each book
# The hidden gem flag is defined as True if the true satisfaction score is greater than 0.6 and
# rating_count is less than the median rating count across all books. 
book_df['hidden_gem_flag'] = (book_df['true_satisfaction'] > 0.6) & (book_df['rating_count'] < book_df['rating_count'].median())

# Replace NaN values with None to ensure compatibility with MongoDB when updating the books collection
book_df['hidden_gem_flag'] = book_df['hidden_gem_flag'].replace({np.nan: None})

# Update MongoDB with the new hidden gem flag
updates = []
for row in book_df.itertuples(index=False):
    updates.append(
        UpdateOne(
            {"book_id": row.book_id},
             {"$set": {"hidden_gem_flag": row.hidden_gem_flag}},
                upsert=False
        )
    )

if updates:
    result = books.bulk_write(updates, ordered=False)
    print(f"Successfully updated {result.modified_count} books with hidden gem flag")

 
