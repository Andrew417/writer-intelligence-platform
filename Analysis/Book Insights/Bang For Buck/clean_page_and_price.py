import pandas as pd
import numpy as np
from pymongo import MongoClient, UpdateOne

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
collection = db["books"]

cursor = collection.find({}, {"_id": 0, "book_id": 1, "page_count": 1,"price": 1,"engagement_depth_score": 1})

df = pd.DataFrame(list(cursor))

# Convert page_count to numeric, coercing errors to NaN
df['page_count'] = df['page_count'].astype(str).str.extract(r'(\d+)').astype(float)

# Extract only the numbers and decimals from the price
df['clean_price'] = df['price'].astype(str).str.extract(r'([\d\.]+)').astype(float)

#Extract the type of currency from the price
df['currency'] = df['price'].astype(str).str.extract(r'([^\d\.]+)', expand=False).str.strip()

# Fix the 'N/A' bug so missing prices just have a missing currency
df['currency'] = df['currency'].replace('N/A', np.nan)

# Fix Convert Pandas NaN to Python None for MongoDB compatibility
df = df.replace({np.nan: None})

updates = []
for row in df.itertuples(index=False):
    updates.append(
        UpdateOne(
            {"book_id": row.book_id},
            {"$set": {
                "page_count": row.page_count,
                "clean_price": row.clean_price,
                "currency": row.currency
            }}
        )
    )

if updates:
    result = collection.bulk_write(updates)
    print(f"Successfully updated {result.modified_count} books.")

 