import pandas as pd
import numpy as np
from pymongo import MongoClient, UpdateOne

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
books = db["books"]
genre_analysis = db["genre_analysis"]

book_cursor = books.find({}, {"_id": 0, "book_id": 1,"genres":1,"true_satisfaction": 1})

book_df = pd.DataFrame(list(book_cursor))

# Explode the genres list to have one genre per row
book_df_exploded = book_df.explode('genres')

# Calculate the standard deviation of true satisfaction for each genre
# The market risk index is defined as the standard deviation of true satisfaction for a genre.
genre_satisfaction_std = book_df_exploded.groupby('genres')['true_satisfaction'].std().reset_index(name='market_risk_index')

# Replace NaN values with None to ensure compatibility with MongoDB when updating the market_trends collection
genre_satisfaction_std = genre_satisfaction_std.replace({np.nan: None})

# Update MongoDB with the new market risk indices
updates = []
for row in genre_satisfaction_std.itertuples(index=False):
    updates.append(
        UpdateOne(
            {"genres": row.genres},
             {"$set": {"market_risk_index": row.market_risk_index}},
                upsert=False
        )
    )

if updates:
    result = genre_analysis.bulk_write(updates, ordered=False)
    print(f"Successfully updated {result.modified_count} genres with market risk index")

 
