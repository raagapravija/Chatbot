import sqlite3
from datetime import datetime
import streamlit as st
import uuid



# Database file will be created in your project directory
DB_PATH = 'chat_history.db'


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chats
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT,
                  user_id TEXT,
                  role TEXT,
                  content TEXT,
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()

def save_message(session_id, user_id, role, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO chats 
                 (session_id, user_id, role, content, timestamp) 
                 VALUES (?, ?, ?, ?, ?)""",
              (session_id, user_id, role, content, datetime.now()))
    conn.commit()
    conn.close()

def get_all_sessions(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""SELECT DISTINCT session_id, MAX(timestamp) as last_used 
                 FROM chats 
                 WHERE user_id = ? 
                 GROUP BY session_id 
                 ORDER BY last_used DESC""", (user_id,))
    sessions = c.fetchall()
    conn.close()
    return [{'session_id': s[0], 'last_used': s[1]} for s in sessions]

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

def get_session_preview(session_id):
    """Get first/last message for preview"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT content FROM chats 
        WHERE session_id = ? 
        ORDER BY timestamp 
        LIMIT 1
    """, (session_id,))
    preview = c.fetchone()[0][:50] + "..." if c.fetchone() else "Empty session"
    conn.close()
    return preview