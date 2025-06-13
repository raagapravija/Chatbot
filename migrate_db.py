import sqlite3
from datetime import datetime

DB_PATH = 'chat_history.db'

def migrate_database():
    print("Starting database migration...")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Check if session_name exists
        c.execute("PRAGMA table_info(chats)")
        columns = [col[1] for col in c.fetchall()]
        
        if 'session_name' not in columns:
            print("Adding session_name column...")
            c.execute("ALTER TABLE chats ADD COLUMN session_name TEXT")
            c.execute("UPDATE chats SET session_name = 'New Chat'")
        
        if 'created_at' not in columns:
            print("Adding created_at column...")
            c.execute("ALTER TABLE chats ADD COLUMN created_at DATETIME")
            c.execute("UPDATE chats SET created_at = ?", (datetime.now(),))
        
        conn.commit()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
