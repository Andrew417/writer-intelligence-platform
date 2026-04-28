import pandas as pd
import numpy as np
from pymongo import MongoClient, UpdateOne

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
books = db["books"]
genre_analysis = db["genre_analysis "]

book_cursor = books.find({}, {"_id": 0, "book_id": 1,"viral_potential_score":1,"days_since_published": 1})

book_df = pd.DataFrame(list(book_cursor))

# Calculate the viral breakout flag for each book
# The viral breakout flag is defined as True if the viral potential score is greater than 0.6 and days_since_published < 1260
book_df['viral_breakout_flag'] = (book_df['viral_potential_score'] > 0.6) & (book_df['days_since_published'] < 1260)

# Replace NaN values with None to ensure compatibility with MongoDB when updating the books collection
book_df['viral_breakout_flag'] = book_df['viral_breakout_flag'].replace({np.nan: None})

# Update MongoDB with the new viral breakout flag
updates = []
for row in book_df.itertuples(index=False):
    updates.append(
        UpdateOne(
            {"book_id": row.book_id},
             {"$set": {"viral_breakout_flag": row.viral_breakout_flag}},
                upsert=False
        )
    )

if updates:
    result = books.bulk_write(updates, ordered=False)
    print(f"Successfully updated {result.modified_count} books with viral breakout flag")

 
