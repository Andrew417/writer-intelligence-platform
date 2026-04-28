import pandas as pd
import numpy as np
from pymongo import MongoClient, UpdateOne

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
collection = db["books"]

cursor = collection.find({}, {"_id": 0, "book_id": 1, "page_count": 1,"clean_price": 1,"engagement_depth_score": 1})

df = pd.DataFrame(list(cursor))

#cleaning data by filling missing values with their median
price_median = df['clean_price'].median(); print(price_median)
page_count_median = df['page_count'].median(); print(page_count_median)

df['clean_price'] = df['clean_price'].fillna(price_median)
df['page_count'] = df['page_count'].fillna(page_count_median)

# Prevent division by zero for free books ($0.00)
df['clean_price'] = df['clean_price'].clip(lower=0.99) 

# Calculate Bang for Buck score
df["bang_for_buck"] = (df["page_count"] * df["engagement_depth_score"])/ df["clean_price"]

# Log transform the Bang for Buck scores to reduce skewness
df["bang_for_buck"] = np.log1p(df["bang_for_buck"])

# Calculate min and max for normalization
min_bfb = df['bang_for_buck'].min()
max_bfb = df['bang_for_buck'].max()

# Apply Relative Min-Max Normalization
df['normalized_bang_for_buck'] = (df['bang_for_buck'] - min_bfb) / (max_bfb - min_bfb)

# Convert Pandas NaN to Python None for MongoDB compatibility
df = df.replace({np.nan: None})

# Update MongoDB with the new normalized Bang for Buck scores
updates = []
for row in df.itertuples(index=False):
    updates.append(
        UpdateOne(
            {"book_id": row.book_id},
            {"$set": {
                "normalized_bang_for_buck": row.normalized_bang_for_buck
            }}
        )
    )

if updates:
    result = collection.bulk_write(updates)
    print(f"Successfully updated {result.modified_count} books with normalized Bang for Buck scores.")

