from pymongo import MongoClient
import pandas as pd

# Connect to MongoDB and select the books database
client = MongoClient("mongodb+srv://karammaria0_db_user:16elMW56jalztyiA@cluster0.s9vsxdk.mongodb.net/")
db = client["books_db"]


# Load review NLP analysis data into a DataFrame
nlp_data = pd.DataFrame(
    list(db.review_nlp_analysis.find())
)
print("Loaded review_nlp_analysis successfully")
print(nlp_data.head())


# Aggregate emotion and sentiment values by book_id
book_summary = nlp_data.groupby("book_id").agg({
    "emotion_intensity": "mean",
    "sentiment_score": "mean",
    "emotion_joy": "mean",
    "emotion_anger": "mean",
    "emotion_sadness": "mean",
    "emotion_fear": "mean",
    "emotion_surprise": "mean"
}).reset_index()

# Rename the columns for clearer output
book_summary.rename(columns={
    "emotion_intensity": "avg_emotion_intensity",
    "sentiment_score": "avg_sentiment_score"
}, inplace=True)


# Find the dominant and secondary emotions for each book

def get_emotions(row):
    emotions = {
        "joy": row["emotion_joy"],
        "anger": row["emotion_anger"],
        "sadness": row["emotion_sadness"],
        "fear": row["emotion_fear"],
        "surprise": row["emotion_surprise"]
    }

    sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
    dominant = sorted_emotions[0][0]
    secondary = sorted_emotions[1][0]

    return dominant, secondary

book_summary[["dominant_emotion", "secondary_emotion"]] = book_summary.apply(
    get_emotions,
    axis=1,
    result_type="expand"
)

# Save the summary to CSV
book_summary.to_csv(
    "book_emotion_summary.csv",
    index=False
)
print("CSV file created successfully")

# Write the aggregated summary back into MongoDB
records = book_summary.to_dict("records")
if len(records) > 0:
    db.book_emotion_summary.delete_many({})
    db.book_emotion_summary.insert_many(records)
    print("MongoDB collection 'book_emotion_summary' updated successfully")
else:
    print("No records found. Nothing inserted.")

print("\nFinal Book Emotion Summary:")
print(book_summary.head())