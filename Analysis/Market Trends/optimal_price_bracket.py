import pandas as pd
import numpy as np
from pymongo import MongoClient, UpdateOne

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
books = db["books"]
market_trends = db["market_trends"]

# Fetch the necessary financial and satisfaction data
book_cursor = books.find({}, {"_id": 0, "book_id": 1,"clean_price":1,"true_satisfaction": 1,"engagement_depth_score": 1})

books_df = pd.DataFrame(list(book_cursor))

# Drop any books that somehow slipped through without a price
books_df = books_df.dropna(subset=['clean_price'])

bins = [-0.01, 4.99, 9.99, 14.99, float('inf')]
labels = ['$0.00 - $4.99', '$5.00 - $9.99', '$10.00 - $14.99', '$15.00+']

# Categorize books into price brackets based on their clean price
books_df['price_bracket'] = pd.cut(books_df['clean_price'], bins=bins, labels=labels, right=True)

# Analyze the average true satisfaction and engagement depth for each price bracket
pricing_analysis = books_df.groupby('price_bracket', observed=False).agg(
    total_books_in_bracket=('book_id', 'count'),
    avg_satisfaction=('true_satisfaction', 'mean'),
    avg_engagement_depth=('engagement_depth_score', 'mean')
).reset_index()

# Replace NaN values with None to ensure compatibility with MongoDB when updating the market_trends collection
pricing_analysis = pricing_analysis.replace({np.nan: None})

# Upsert the price bracket analysis results into the market_trends collection
updates = []
for row in pricing_analysis.itertuples(index=False):
    # Only save brackets that actually have books in them
    if row.total_books_in_bracket > 0:
        updates.append(
            UpdateOne(
                {
                    "trend_type": "pricing_bracket", 
                    "bracket_name": row.price_bracket
                },
                {"$set": {
                    "total_books_in_bracket": row.total_books_in_bracket,
                    "avg_satisfaction": row.avg_satisfaction,
                    "avg_engagement_depth": row.avg_engagement_depth
                }},
                upsert=True
            )
        )

if updates:
    result = market_trends.bulk_write(updates, ordered=False)
    print(f"Successfully upserted {len(updates)} price brackets into market_trends.")