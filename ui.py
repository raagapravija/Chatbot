import streamlit as st
import uuid
from db_utils import get_all_sessions, get_session_messages, delete_session

def load_session(session_id):
    """Load a specific chat session from database"""
    try:
        st.session_state.session_id = session_id
        st.session_state.messages = get_session_messages(session_id)
        st.rerun()
    except Exception as e:
        st.error(f"Failed to load session: {str(e)}")
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Sorry, I couldn't load that conversation"
        }]

def start_new_session():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! How can I help you today?"
    }]
    st.rerun()

def setup_page_config(config):
    st.set_page_config(**config)

def apply_custom_styles():
    st.markdown("""
    <style>
    /* Clean light background */
    .stApp {
        background: #f8f9fc;
        background-attachment: fixed;
    }
    
    /* Header styling */
    .header {
        text-align: center;
        padding: 1.2rem 0;
        margin: -1rem -1rem 1.5rem -1rem;
        background: white;
        border-radius: 0 0 24px 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }
    
    /* USER BUBBLE - Crisp white */
    .user-message {
        background: white;
        color: #2d3748;
        border: 1px solid #e2e8f0;
        border-radius: 22px 22px 0 22px;
        padding: 16px 20px;
        margin: 12px 0;
        margin-left: auto;
        max-width: 80%;
        word-wrap: break-word;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        line-height: 1.5;
    }
    
    /* AI BUBBLE - Soft dark gray */
    .assistant-message {
        background: #2d3748;
        color: #f8fafc;
        border-radius: 22px 22px 22px 0;
        padding: 16px 20px;
        margin: 12px 0;
        margin-right: auto;
        max-width: 80%;
        word-wrap: break-word;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        line-height: 1.5;
        border: 1px solid #3c4658;
    }
    
    /* Chat container */
    .chat-message {
        width: 100%;
        display: flex;
        animation: fadeInUp 0.35s cubic-bezier(0.15, 0.85, 0.35, 1);
    }
    
    /* Input field */
    .stChatInput {
        position: fixed;
        bottom: 20px;
        width: 75%;
        left: 12.5%;
        background: white;
        border-radius: 24px;
        padding: 14px 24px;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
                
    .stButton>button {
    transition: all 0.3s ease;
    }
                
    .stButton>button:hover {
    transform: scale(1.05);
    }
                
    # New chat button
    .stButton>button:has(> div>div>svg[data-testid="NewChatIcon"]) {
        background: linear-gradient(135deg, #6e8efb, #a777e3);
    }
    
    /* Spinner color */
    .stSpinner > div {
        margin-right: auto;
        color: #2d3748 !important;
    }
    
    /* Animation */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #edf2f7;
    }
    ::-webkit-scrollbar-thumb {
        background: #cbd5e0;
        border-radius: 3px;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .stChatInput {
            width: 90%;
            left: 5%;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def display_header():
    st.markdown("""
        <div class="header">
            <h1 style="margin:0; color:#4a5568; font-weight:600;">✨ AI Assistant</h1>
        </div>
    """, unsafe_allow_html=True)

def display_message(role, content):
    message_class = "user-message" if role == "user" else "assistant-message"
    st.markdown(f"""
        <div class="chat-message">
            <div class="{message_class}">
                {content}
            </div>
        </div>
    """, unsafe_allow_html=True)

def history_sidebar():
    with st.sidebar:
        st.markdown("## ✨ Chat", unsafe_allow_html=True)

        if 'user_id' not in st.session_state or 'session_id' not in st.session_state:
            start_new_session()
            return

        sessions = get_all_sessions(st.session_state.user_id)

        # Reverse sessions so most recent shows on top
        sessions = list(reversed(sessions))

        current_session = st.session_state.session_id

        for idx, s in enumerate(sessions):
            session_id = s["session_id"]
            session_number = idx + 1
            is_current = session_id == current_session

            cols = st.columns([0.8, 0.2])
            with cols[0]:
                st.markdown(
                    f"""
                    <div style='padding: 8px; border-radius: 8px; background-color: {"#e2e8f0" if is_current else "transparent"}; cursor: pointer;'>
                        <span style='font-size: 15px;'> Session {session_number}</span><br>
                        <small style='color: gray;'>{session_id[:8]}...</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(f"Switch to Session {session_number}", key=f"load_{session_id}"):
                    load_session(session_id)

            with cols[1]:
                with st.popover("⋮"):
                    if st.button("🗑️ Delete", key=f"delete_{session_id}"):
                        delete_session(session_id)
                        st.rerun()

        st.markdown("---")
        if st.button(" New Chat", type="primary"):
            start_new_session()

