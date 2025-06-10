import os
import streamlit as st
from langchain_community.llms import DeepInfra
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up the page
st.set_page_config(page_title="Chatbot", page_icon="🤖")
st.title("💬 AI Chatbot (Working Version)")

# Initialize the LLM with correct parameters
@st.cache_resource
def load_llm():
    return DeepInfra(
        model_id="mistralai/Mistral-7B-Instruct-v0.1",
        model_kwargs={
            "temperature": 0.7,
            "max_new_tokens": 200,
            "top_p": 0.9
        }
    )

# Check API key
if not os.getenv("DEEPINFRA_API_TOKEN"):
    st.error("❌ Missing DeepInfra API key in .env file")
    st.info("Get a free key from: https://deepinfra.com/")
    st.stop()

# Set API key as environment variable
os.environ["DEEPINFRA_API_TOKEN"] = os.getenv("DEEPINFRA_API_TOKEN")

# Initialize chat
try:
    llm = load_llm()
    st.success("✅ Chatbot initialized successfully!")
except Exception as e:
    st.error(f"Initialization failed: {str(e)}")
    st.stop()

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User input
if prompt := st.chat_input("Ask me anything"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        try:
            response = llm.invoke(prompt)
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error("⚠️ Error generating response")
            st.info("Try a simpler question or wait a minute")