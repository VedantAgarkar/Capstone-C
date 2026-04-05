import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "users.db")

def get_db_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database with the users table."""
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            fullname TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')

    # Ensure is_admin column exists if table was already created
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        # Column already exists
        pass

    # Create predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT NOT NULL,
            inputs TEXT NOT NULL,
            outcome TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def log_prediction(email, prediction_type, inputs, outcome):
    """
    Logs a prediction result to the database.
    Inputs is expected to be a JSON-serializable dict or list, or a string.
    """
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        user_id = None
        if email:
            email = email.strip().lower()
            cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email,))
            row = cursor.fetchone()
            if row:
                user_id = row['id']
            else:
                pass # Silently handle no user found for email
        else:
            pass # Silently handle guest predictions
        
        # Ensure inputs is a string
        if not isinstance(inputs, str):
            inputs = json.dumps(inputs)
            
        cursor.execute('''
            INSERT INTO predictions (user_id, type, inputs, outcome)
            VALUES (?, ?, ?, ?)
        ''', (user_id, prediction_type, inputs, outcome))
        conn.commit()
    except Exception as e:
        print(f"Database Error in log_prediction: {e}")
    finally:
        conn.close()

def get_user_predictions(email):
    """Retrieves all predictions for a specific user email."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        email = email.strip().lower()
        cursor.execute("""
            SELECT p.* FROM predictions p 
            JOIN users u ON p.user_id = u.id 
            WHERE LOWER(u.email) = ? 
            ORDER BY timestamp DESC
        """, (email,))
        return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Database Error in get_user_predictions: {e}")
        return []
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
