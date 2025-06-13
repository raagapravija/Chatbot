import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()


# LLM Configuration
LLM_CONFIG = {
    "model_id": "mistralai/Mistral-7B-Instruct-v0.1",
    "model_kwargs": {
        "temperature": 0.6,
        "max_new_tokens": 500,
        "top_p": 0.9,
        "repetition_penalty": 1.1,
        "stop_sequences": ["\nUser:", "\nHuman:", "###"]
    }
}

# API Configuration
API_TOKEN = os.getenv("DEEPINFRA_API_TOKEN")
if not API_TOKEN:
    raise ValueError("❌ Missing DeepInfra API token")

os.environ["DEEPINFRA_API_TOKEN"] = API_TOKEN

# App Configuration
APP_CONFIG = {
    "page_title": "Mistral Chat",
    "page_icon": "✨",
    "layout": "wide",
    "initial_sidebar_state": "collapsed"
}

def set_streamlit_config():
    st.set_page_config(
        initial_sidebar_state="expanded",  # This makes sidebar open by default
        layout="wide"
    )