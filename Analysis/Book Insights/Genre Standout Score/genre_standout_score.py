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
genre_cursor = genre_analysis.find({}, {"_id": 0, "genres": 1, "avg_satisfaction": 1})

book_df = pd.DataFrame(list(book_cursor))
genre_df = pd.DataFrame(list(genre_cursor))

# Explode the genres list to have one genre per row
book_df_exploded = book_df.explode('genres')


# Merge the exploded book dataframe with the genre summary table.
merged_df = pd.merge(book_df_exploded, genre_df, on='genres', how='left')

# drop rows where avg_satisfaction is null (i.e., genres that were not found in the genre summary table)
merged_df = merged_df.dropna(subset=['avg_satisfaction'])

# Calculate the standout score for each book-genre pair
# The standout score is defined as the ratio of the book's true satisfaction to the average satisfaction of its genre.
# A standout score greater than 1 indicates that the book is performing better than the average for its genre,
#  while a score less than 1 indicates it is performing worse.
merged_df['standout_score'] = merged_df['true_satisfaction'] / merged_df['avg_satisfaction']




# Create the array of {genre, standout_score} objects for each book
def create_genre_score_array(group):
    """Create array of {genre: genre_name, standout_score: score} for each book"""
    # Using index=False because we don't need the dataframe index for this
    return [
        {"genre": row.genres, "standout_score": row.standout_score} 
        for row in group.itertuples(index=False)
    ]

# Group by book_id and create the array structure you want
standout_scores_df = merged_df.groupby('book_id').apply(create_genre_score_array).reset_index(name='standout_scores')

# Now i want the highest standout score and its genre to be concatenated into a string and added as new field "top_genre_standout_score" in the standout_scores_df dataframe
def get_top_genre_standout_score(genre_scores):
    """Get the genre with the highest standout score and format it as 'Genre: Score'"""
    if not genre_scores:
        return None  # Handle case where there are no genres
    top_genre = max(genre_scores, key=lambda x: x['standout_score'])
    return f"{top_genre['genre']}: {top_genre['standout_score']:.2f}"

standout_scores_df['top_genre_standout_score'] = standout_scores_df['standout_scores'].apply(get_top_genre_standout_score)

# Update MongoDB with the new normalized timelessness scores
updates = []
for row in standout_scores_df.itertuples(index=False):
    updates.append(
        UpdateOne(
            {"book_id": row.book_id},
             {"$set": {"standout_scores": row.standout_scores, "top_genre_standout_score": row.top_genre_standout_score}},
                upsert=False
        )
    )

if updates:
    result = books.bulk_write(updates, ordered=False)
    print(f"Successfully updated {result.modified_count} books")

 
