# app.py
import streamlit as st
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize LangChain
llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0.7)
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory)

# Page config
st.set_page_config(page_title="🧠 Chat with LangChain", page_icon="🤖", layout="centered")
st.markdown("<h1 style='text-align: center;'>💬 LangChain Chatbot</h1>", unsafe_allow_html=True)
st.markdown("---")

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_input = st.text_input("Type your message here...", key="input")

# When send button is clicked
if st.button("Send", use_container_width=True):
    if user_input:
        # LangChain generates response
        response = conversation.predict(input=user_input)

        # Save to history
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("bot", response))

# Display chat bubbles
for speaker, message in st.session_state.chat_history:
    if speaker == "user":
        st.markdown(f"<div style='background-color:#DCF8C6; padding:10px; border-radius:10px; margin-bottom:5px; text-align:right'>{message}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background-color:#F1F0F0; padding:10px; border-radius:10px; margin-bottom:10px; text-align:left'>{message}</div>", unsafe_allow_html=True)
