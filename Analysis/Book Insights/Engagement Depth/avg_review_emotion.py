from pymongo import MongoClient, UpdateOne
 


# 1. Connect to MongoDB
client = MongoClient("mongodb+srv://maroamgad12345_db_user:CUSoEyXSXSIoBIB6@cluster0.s9vsxdk.mongodb.net/books")
db = client["books_db"]
collection = db["review_nlp_analysis"]


pipeline = [
    # Compute Emotion per review
    {
        "$project": {
            "book_id": 1,
            "Emotion": {
                "$add": [
                    {"$multiply": ["$emotion_intensity", 0.7]},
                    {
                        "$multiply": [
                            {
                                "$divide": [
                                    {
                                        "$add": [
                                            "$emotion_joy",
                                            "$emotion_sadness",
                                            "$emotion_anger",
                                            "$emotion_fear",
                                            "$emotion_surprise"
                                        ]
                                    },
                                    5
                                ]
                            },
                            0.3
                        ]
                    }
                ]
            }
        }
    },

    # Aggregate per book (THIS FIXES YOUR ISSUE)
    {
        "$group": {
            "_id": "$book_id",
            "Emotion": { "$avg": "$Emotion" }  # average across reviews
        }
    },

    # Reshape and Rename for merge
    {
        "$project": {
            "_id": 0,
            "book_id": "$_id",
            "avg_review_emotion": "$Emotion"
        }
    },

    # Merge into books collection
    {
        "$merge": {
            "into": "books",
            "on": "book_id",
            "whenMatched": "merge",
            "whenNotMatched": "discard"
        }
    }
]

collection.aggregate(pipeline)
print("Average review emotion computed and merged into books collection successfully.")
