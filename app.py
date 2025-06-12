import streamlit as st
import uuid
from ui import setup_page_config, apply_custom_styles, display_header, display_message, history_sidebar
from llm_utils import load_llm, initialize_chat_session
from chat_utils import generate_response
from config import APP_CONFIG
from db_utils import init_db, save_message, get_session_messages, get_all_sessions

def main():
    # Setup UI first
    setup_page_config(APP_CONFIG)
    apply_custom_styles()
    display_header()
    
    # Initialize database
    init_db()
    
    # Initialize session state variables
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if 'messages' not in st.session_state:
        st.session_state.messages = get_session_messages(st.session_state.session_id) or [{
            "role": "assistant", 
            "content": "Hello! How can I help you today?"
        }]
    
    # Initialize LLM
    try:
        llm = load_llm()
    except Exception as e:
        st.error(f"LLM initialization error: {str(e)}")
        st.stop()
    
    # Show history sidebar
    history_sidebar()
    
    # Display chat history
    for msg in st.session_state.messages:
        display_message(msg["role"], msg["content"])
    
    # Handle user input
    if prompt := st.chat_input("Ask me anything..."):
        # Save and display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        display_message("user", prompt)
        save_message(
            session_id=st.session_state.session_id,
            user_id=st.session_state.user_id,
            role="user",
            content=prompt
        )
        
        # Generate and save assistant response
        with st.spinner("Thinking..."):
            try:
                response = generate_response(llm, prompt, st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": response})
                display_message("assistant", response)
                save_message(
                    session_id=st.session_state.session_id,
                    user_id=st.session_state.user_id,
                    role="assistant",
                    content=response
                )
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                display_message("assistant", error_msg)

if __name__ == "__main__":
    main()