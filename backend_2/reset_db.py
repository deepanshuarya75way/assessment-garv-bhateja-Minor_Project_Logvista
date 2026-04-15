import sqlite3
from werkzeug.security import generate_password_hash
import os

DB_FILE = "logvista.db"

def reset_db():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Deleted old database: {DB_FILE}")
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Create Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Create Logs Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source TEXT,
            event TEXT,
            severity TEXT,
            status TEXT,
            raw TEXT,
            hash TEXT
        )
    ''')
    
    # Create Threats Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS threats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            reasoning TEXT,
            confidence INTEGER,
            impact TEXT,
            mitigation TEXT,
            log_samples TEXT
        )
    ''')
    
    # Create Timeline Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            log TEXT,
            attack TEXT,
            phase TEXT,
            type TEXT
        )
    ''')

    # Create Incidents Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT,
            ip TEXT,
            user TEXT,
            risk_score INTEGER,
            start_time TEXT,
            global_attack TEXT
        )
    ''')

    # Create Story Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS story (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sentence TEXT
        )
    ''')
    
    # Seed Admin User
    hashed_pw = generate_password_hash('password')
    c.execute("INSERT INTO users (username, password_hash) VALUES ('admin', ?)", (hashed_pw,))
    
    conn.commit()
    conn.close()
    print("New database initialized with COMPLETE schema and admin user.")

if __name__ == "__main__":
    reset_db()
