import streamlit as st
from pymongo import MongoClient
import certifi
import os

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
        st.error("❌ MongoDB connection string not found. Set secrets in Streamlit Cloud or .env locally.")
        st.stop()

    # Connect with SSL certificate bundle
    client = MongoClient(
        uri,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=15000,
        tls=True,
        tlsAllowInvalidCertificates=True
    )

    try:
        client.admin.command("ping")
    except Exception as e:
        get_database.clear()
        st.error(f"❌ Failed to connect to MongoDB: {e}")
        st.stop()

    return client[db_name]