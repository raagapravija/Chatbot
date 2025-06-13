from langchain_groq import ChatGroq
from config import Config
import streamlit as st

@st.cache_resource
def load_llm():
    return ChatGroq(
        temperature=0.7,
        model_name=Config.ACTIVE_MODEL,  # Use the new model
        api_key=Config.GROQ_API_KEY
    )

def initialize_chat_session():
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant", 
            "content": "Hello! How can I help you today?"
        }]