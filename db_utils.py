import sqlite3
from datetime import datetime
import streamlit as st
import uuid

# Database file created in project directory
DB_PATH = 'chat_history.db'


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create initial table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS chats
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT,
                  user_id TEXT,
                  role TEXT,
                  content TEXT,
                  timestamp DATETIME)''')
    
    # Check if columns exist and add them if needed
    c.execute("PRAGMA table_info(chats)")
    columns = [col[1] for col in c.fetchall()]
    
    if 'session_name' not in columns:
        try:
            # First add without default
            c.execute("ALTER TABLE chats ADD COLUMN session_name TEXT")
            # Then update all existing rows
            c.execute("UPDATE chats SET session_name = 'New Chat'")
        except sqlite3.OperationalError:
            pass
    
    if 'created_at' not in columns:
        try:
            # First add without default
            c.execute("ALTER TABLE chats ADD COLUMN created_at DATETIME")
            # Then update all existing rows with current timestamp
            c.execute("UPDATE chats SET created_at = datetime('now')")
        except sqlite3.OperationalError:
            pass
    
    # Create indexes
    c.execute("CREATE INDEX IF NOT EXISTS idx_session ON chats (session_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_user ON chats (user_id)")
    
    conn.commit()
    conn.close()

def save_message(session_id, user_id, role, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if this is the first message in the session
    c.execute("SELECT COUNT(*) FROM chats WHERE session_id = ?", (session_id,))
    is_first_message = c.fetchone()[0] == 0
    
    if is_first_message:
        # For the first message, set created_at and default session name
        c.execute("""INSERT INTO chats 
                     (session_id, user_id, role, content, timestamp, session_name, created_at) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (session_id, user_id, role, content, datetime.now(), "New Chat", datetime.now()))
    else:
        # For subsequent messages, just insert the basic info
        c.execute("""INSERT INTO chats 
                     (session_id, user_id, role, content, timestamp) 
                     VALUES (?, ?, ?, ?, ?)""",
                  (session_id, user_id, role, content, datetime.now()))
    
    conn.commit()
    conn.close()

def get_all_sessions(user_id):
    """Returns sessions with proper datetime objects"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    c = conn.cursor()
    c.execute("""
        SELECT 
            session_id, 
            datetime(MAX(timestamp), 'localtime') as last_used
        FROM chats 
        WHERE user_id = ? 
        GROUP BY session_id 
        ORDER BY last_used DESC
    """, (user_id,))
    sessions = [dict(row) for row in c.fetchall()]  # Convert to dictionaries
    conn.close()
    return sessions
def get_session_messages(session_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""SELECT role, content, timestamp 
                 FROM chats 
                 WHERE session_id = ? 
                 ORDER BY timestamp""", (session_id,))
    messages = [{'role': row[0], 'content': row[1], 'timestamp': row[2]} 
               for row in c.fetchall()]
    conn.close()
    return messages

def delete_session(session_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM chats WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

def update_session_name(session_id, new_name):
    """Update the session name for all records of this session"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Update session_name for all messages in this session
    c.execute("""UPDATE chats 
                 SET session_name = ?
                 WHERE session_id = ?""",
              (new_name, session_id))
    
    conn.commit()
    conn.close()

def get_session_preview(session_id):
    """Get the first user message as preview"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT content FROM chats 
        WHERE session_id = ? AND role = 'user' 
        ORDER BY timestamp ASC 
        LIMIT 1
    """, (session_id,))
    result = c.fetchone()
    conn.close()
    return result[0][:30] + "..." if result else "New Chat"