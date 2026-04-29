import streamlit as st
from pymongo import MongoClient
import certifi
import os
import ssl

@st.cache_resource
def get_database():
    uri = None
    db_name = None

    # Try Streamlit Cloud secrets first
    try:
        uri = st.secrets["MONGO_URI"]
        db_name = st.secrets["MONGO_DB"]
    except Exception:
        pass

    # Fallback to .env for local development
    if not uri:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            uri = os.getenv("MONGO_URI")
            db_name = os.getenv("MONGO_DB")
        except Exception:
            pass

    if not uri:
        st.error("❌ MongoDB connection string not found.")
        st.stop()

    # Try multiple connection methods until one works
    connection_attempts = [
        {
            "name": "Standard + certifi",
            "kwargs": {
                "tlsCAFile": certifi.where(),
                "serverSelectionTimeoutMS": 15000,
            }
        },
        {
            "name": "Allow invalid certificates",
            "kwargs": {
                "tls": True,
                "tlsAllowInvalidCertificates": True,
                "serverSelectionTimeoutMS": 15000,
            }
        },
        {
            "name": "certifi + allow invalid",
            "kwargs": {
                "tlsCAFile": certifi.where(),
                "tlsAllowInvalidCertificates": True,
                "serverSelectionTimeoutMS": 15000,
            }
        },
        {
            "name": "No TLS verification",
            "kwargs": {
                "tls": True,
                "tlsInsecure": True,
                "serverSelectionTimeoutMS": 15000,
            }
        },
    ]

    for attempt in connection_attempts:
        try:
            client = MongoClient(uri, **attempt["kwargs"])
            client.admin.command("ping")
            return client[db_name]
        except Exception:
            continue

    # If all methods failed, clear cache and show error
    get_database.clear()
    st.error("❌ Failed to connect to MongoDB after all attempts. Check your connection string and network.")
    st.stop()