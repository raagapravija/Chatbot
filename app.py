import os
import streamlit as st
from langchain_community.llms import DeepInfra
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up the page
st.set_page_config(page_title="Chatbot", page_icon="🤖")
st.title("💬 Expert AI Assistant")

# Initialize the LLM with optimized parameters
@st.cache_resource
def load_llm():
    return DeepInfra(
        model_id="mistralai/Mistral-7B-Instruct-v0.1",
        model_kwargs={
            "temperature": 0.5,  # Balanced between creative and factual
            "max_new_tokens": 250,
            "top_p": 0.85,
            "repetition_penalty": 1.05,
            "stop_sequences": ["\nUser:", "\nHuman:", "###"]
        }
    )

# Check API key
if not os.getenv("DEEPINFRA_API_TOKEN"):
    st.error("❌ Missing DeepInfra API key")
    st.stop()

os.environ["DEEPINFRA_API_TOKEN"] = os.getenv("DEEPINFRA_API_TOKEN")

# Enhanced response generation
def generate_response(prompt, history):
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-3:]])
    
    instruction = f"""You are a knowledgeable AI assistant. Provide clear, confident answers to technical questions.
If a question is unclear, ask for clarification once. Otherwise, answer directly.

Conversation context:
{context}
User: {prompt}
Assistant:"""
    
    try:
        response = llm.invoke(instruction)
        response = response.split("\n")[0].strip()
        
        # More permissive validation
        if not response or response.startswith(("I don't know", "I'm not sure")):
            return "Could you provide more details about what you're looking for?"
        return response
        
    except Exception as e:
        return "Let me try that again. " + prompt.split("?")[0] + "?"

# Initialize chat
try:
    llm = load_llm()
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant", 
            "content": "I'm an AI technical assistant. Ask me about programming, AI, or data science!"
        }]
except Exception as e:
    st.error(f"Initialization error: {str(e)}")
    st.stop()

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle user input
if prompt := st.chat_input("Ask a technical question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            response = generate_response(prompt, st.session_state.messages)
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})