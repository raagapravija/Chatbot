import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Configuration Constants
APP_CONFIG = {
    "page_title": "AI Assistant",
    "page_icon": "✨",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "mixtral-8x7b-32768"
    ACTIVE_MODEL = "llama3-70b-8192"
    
    if not GROQ_API_KEY:
        raise ValueError("❌ GROQ_API_KEY missing from .env")

def set_streamlit_config():
    """Centralized Streamlit configuration"""
    st.set_page_config(**APP_CONFIG)