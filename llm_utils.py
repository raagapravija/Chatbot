from langchain_community.llms import DeepInfra
import streamlit as st
from config import LLM_CONFIG

@st.cache_resource
def load_llm():
    return DeepInfra(
        model_id=LLM_CONFIG["model_id"],
        model_kwargs=LLM_CONFIG["model_kwargs"]
    )

def initialize_chat_session():
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant", 
            "content": "Hello! I'm your AI assistant. How can I help you today?"
        }]