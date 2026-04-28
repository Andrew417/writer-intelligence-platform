import streamlit as st
from pymongo import MongoClient
import certifi
import os

@st.cache_resource
def get_database():
    try:
        uri = st.secrets["MONGO_URI"]
        db_name = st.secrets["MONGO_DB"]
    except Exception:
        from dotenv import load_dotenv
        load_dotenv()
        uri = os.getenv("MONGO_URI")
        db_name = os.getenv("MONGO_DB")

    if not uri:
        st.error("❌ MongoDB connection string not found.")
        st.stop()

    # Fix SSL issue with certifi
    client = MongoClient(uri, tlsCAFile=certifi.where())

    try:
        client.admin.command("ping")
    except Exception as e:
        st.error(f"❌ Failed to connect to MongoDB: {e}")
        st.stop()

    return client[db_name]