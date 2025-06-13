import streamlit as st
import uuid
from ui import setup_page_config, apply_custom_styles, display_header, display_message, history_sidebar
from llm_utils import load_llm
from chat_utils import generate_response
from db_utils import init_db, save_message, get_session_messages
from config import set_streamlit_config

def main():
    # Initialize app configuration
    set_streamlit_config()
    
    # Setup UI
    apply_custom_styles()
    display_header()
    
    # Initialize database
    init_db()
    
    # Initialize session state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = [{
            "role": "assistant", 
            "content": "Hello! How can I help you today?"
        }]
    elif 'messages' not in st.session_state:
        st.session_state.messages = get_session_messages(st.session_state.session_id) or [{
            "role": "assistant",
            "content": "Hello! How can I help you today?"
        }]
    
    # Show sidebar
    history_sidebar()
    
    # Display messages
    for msg in st.session_state.messages:
        display_message(msg["role"], msg["content"])
    
    # Handle user input
    if prompt := st.chat_input("Ask me anything..."):
        # Save user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_message(
            session_id=st.session_state.session_id,
            user_id=st.session_state.user_id,
            role="user",
            content=prompt
        )
        
        # Generate response with error handling
        with st.spinner("Thinking..."):
            try:
                response = generate_response(
                    prompt=prompt,
                    history=st.session_state.messages
                )
                
                # Save and display AI response
                st.session_state.messages.append({"role": "assistant", "content": response})
                save_message(
                    session_id=st.session_state.session_id,
                    user_id=st.session_state.user_id,
                    role="assistant",
                    content=response
                )
            except Exception as e:
                if "model_decommissioned" in str(e):
                    # Special handling for deprecated model error
                    error_msg = "System is upgrading its AI model. Please refresh the page."
                    # Optionally add automatic refresh:
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    st.experimental_rerun()
                else:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

        # Rerun to update UI
        st.rerun()

if __name__ == "__main__":
    main()