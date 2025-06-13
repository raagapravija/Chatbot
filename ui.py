import streamlit as st
import uuid
from datetime import datetime
from db_utils import get_all_sessions, get_session_messages, delete_session, update_session_name, get_session_preview 
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def set_sidebar_default_expanded():
    st.markdown("""
    <style>
        [data-testid="collapsedControl"] {
            display: none
        }
    </style>
    """, unsafe_allow_html=True)

def generate_session_name(messages):
    """Generate a meaningful session name based on conversation content"""
    try:
        # Only consider the first few messages to generate the name
        relevant_messages = messages[:4]
        
        # Extract user messages
        user_messages = [msg['content'] for msg in relevant_messages if msg['role'] == 'user']
        if not user_messages:
            return "New Chat"
        
        # Create a prompt for generating the session name
        prompt = ChatPromptTemplate.from_template(
            """Based on the following conversation snippets, generate a concise (3-5 word) 
            title that summarizes the main topic. Return ONLY the title, nothing else.

            Conversation snippets:
            {snippets}

            Title:"""
        )
        
        # Use a simple LLM chain to generate the name
        chain = prompt | StrOutputParser()
        name = chain.invoke({"snippets": "\n".join(user_messages[:3])})
        
        # Clean up the response
        name = name.strip().replace('"', '').replace("'", "")
        if not name or len(name) > 50:  # Fallback if name is empty or too long
            return "New Chat"
        return name
    except Exception:
        return "New Chat"

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
    config["initial_sidebar_state"] = "expanded"
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
    
    
    /* New Chat button styling - matches assistant bubble */
    div.stButton > button:first-child {
        background-color: #2d3748 !important;
        color: #f8fafc !important;
        border: 1px solid #3c4658 !important;
        border-radius: 22px !important;
        padding: 8px 16px !important;
    }
    
    /* Hover effect */
    div.stButton > button:first-child:hover {
        background-color: #3c4658 !important;
        transform: scale(1.05);
        transition: all 0.3s ease;
    }
    
    /* Focus state */
    div.stButton > button:first-child:focus {
        box-shadow: 0 0 0 0.2rem rgba(45, 55, 72, 0.5);
    }
                
    .stButton>button {
        transition: all 0.3s ease;
    }
                
    .stButton>button:hover {
        transform: scale(1.05);
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
    
    /* Updated Chat Input positioning */
    .stChatInput {
        position: fixed;
        bottom: 20px;
        left: calc(300px + 5%);  /* 300px for sidebar + 5% margin */
        width: calc(90% - 300px); /* Adjust width accounting for sidebar */
        background: white;
        border-radius: 24px;
        padding: 14px 24px;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        z-index: 100;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .stChatInput {
            left: 5%;
            width: 90%;
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
    set_sidebar_default_expanded()
    st.markdown("""
    <style>
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        section[data-testid="stSidebar"] {
            width: 300px !important;
        }
        /* Prevent sidebar from collapsing on mobile */
        @media (max-width: 768px) {
            section[data-testid="stSidebar"] {
                width: 300px !important;
                transform: translateX(0) !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("## Chat History")
        
        # Initialize session if needed
        if 'user_id' not in st.session_state:
            st.session_state.user_id = str(uuid.uuid4())
        if 'session_id' not in st.session_state:
            start_new_session()
            return

        try:
            sessions = get_all_sessions(st.session_state.user_id)
        except Exception as e:
            st.error(f"Error loading history: {str(e)}")
            sessions = []

        current_session = st.session_state.session_id

        if not sessions:
            st.info("No previous conversations")
        else:
            for session in sessions:
                preview = get_session_preview(session['session_id'])
                last_used = session['last_used']
                
                # Format timestamp properly
                if isinstance(last_used, str):
                    try:
                        # If it's already a string, parse it
                        from datetime import datetime
                        last_used = datetime.strptime(last_used, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        last_used = "Unknown"
                
                time_str = last_used.strftime("%b %d, %H:%M") if hasattr(last_used, 'strftime') else "Unknown"
                
                cols = st.columns([0.8, 0.2])
                with cols[0]:
                    st.markdown(
                        f"""
                        <div style='padding: 8px; border-radius: 8px; 
                            background-color: {"#f0f4f8" if session['session_id'] == current_session else "transparent"};
                            margin-bottom: 8px;'>
                            <div style='font-weight: 500;'>{preview}</div>
                            <div style='font-size: 0.8em; color: #64748b;'>{time_str}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    if st.button("Switch", key=f"switch_{session['session_id']}"):
                        load_session(session['session_id'])

                with cols[1]:
                    if st.button("🗑️", key=f"delete_{session['session_id']}"):
                        delete_session(session['session_id'])
                        if session['session_id'] == current_session:
                            start_new_session()
                        st.rerun()

        if st.button("+ New Chat", type="primary"):
            start_new_session()
        
        st.components.v1.html("""
        <script>
            setTimeout(function() {
                const sidebar = window.parent.document.querySelector('section[data-testid="stSidebar"]');
                if (sidebar) {
                    sidebar.style.transform = 'none';
                    sidebar.style.visibility = 'visible';
                    sidebar.style.width = '300px';
                }
            }, 100);
        </script>
        """)
        st.components.v1.html("""
        <script>
            function adjustChatInput() {
                const sidebar = document.querySelector('section[data-testid="stSidebar"]');
                const chatInput = document.querySelector('.stChatInput');
                
                if (sidebar && chatInput) {
                    const sidebarWidth = sidebar.offsetWidth;
                    chatInput.style.left = `${sidebarWidth + 20}px`;
                    chatInput.style.width = `calc(100% - ${sidebarWidth + 40}px`;
                }
            }
            
            // Run on load and when window resizes
            window.addEventListener('load', adjustChatInput);
            window.addEventListener('resize', adjustChatInput);
            
            // Also run when sidebar is toggled
            const observer = new MutationObserver(adjustChatInput);
            observer.observe(document.body, { attributes: true, subtree: true });
        </script>
        """)

def chat_interface():
    """Main chat interface with automatic session naming"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        display_message(message['role'], message['content'])

    # After each message exchange, update the session name if it's still the default
    if len(st.session_state.messages) >= 2 and 'session_id' in st.session_state:
        sessions = get_all_sessions(st.session_state.user_id)
        current_session = next((s for s in sessions if s["session_id"] == st.session_state.session_id), None)
        
        if current_session and (not current_session.get("session_name") or 
                              current_session["session_name"] == "New Chat"):
            new_name = generate_session_name(st.session_state.messages)
            if new_name != "New Chat":
                update_session_name(st.session_state.session_id, new_name)
                st.rerun()

def initialize_app(page_config):
    """Initialize the app with page config and session state"""
    # Must be first Streamlit command
    setup_page_config(page_config)
    
    # Then apply other initializations
    set_sidebar_default_expanded()
    apply_custom_styles()
    display_header()

    # Initialize session state if not already set
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    if 'session_id' not in st.session_state:
        start_new_session()