import pandas as pd
import numpy as np
from pymongo import MongoClient, UpdateOne

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
collection = db["books"]

cursor = collection.find({}, {"_id": 0, "book_id": 1, "publication_info": 1,"true_satisfaction": 1})

df = pd.DataFrame(list(cursor))

# Extract the publication date from the publication_info field  
df['published_date'] = df['publication_info'].str.extract(r'(?:First p|P)ublished (.*)')

# Convert the published_date to datetime format
df['published_date'] = pd.to_datetime(df['published_date'], errors='coerce')

# Calculate the number of days since publication for each book
df['days_since_published'] = (pd.Timestamp.today() - df['published_date']).dt.days

# Handle missing values in days_since_published by filling them with the median
days_since_published_median = df['days_since_published'].median(); print(days_since_published_median)
df['days_since_published'] = df['days_since_published'].fillna(days_since_published_median) 


# Log transform the days_since_published to reduce skewness
df['log_days_since_published'] = np.log1p(df['days_since_published'])

df['timelessness'] = df['log_days_since_published'] * df['true_satisfaction']

# Calculate min and max for normalization
min_days = df['timelessness'].min()
max_days = df['timelessness'].max()

# Apply Relative Min-Max Normalization
if max_days > min_days:
    df['normalized_timelessness'] = (df['timelessness'] - min_days) / (max_days - min_days)

# Update MongoDB with the new normalized timelessness scores
updates = []
for row in df.itertuples(index=False):
    updates.append(
        UpdateOne(
            {"book_id": row.book_id},
            {"$set": {
                "normalized_timelessness": row.normalized_timelessness,
                "days_since_published": row.days_since_published
            }}
        )
    )

if updates:
    result = collection.bulk_write(updates)
    print(f"Successfully updated {result.modified_count} books with normalized Timelessness scores.")

 


