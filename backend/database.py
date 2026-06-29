"""
Database setup for storing embeddings and queries
"""

import sqlite3
import json
from backend.config import DATABASE_PATH

def init_database():
    """Initialize SQLite database"""
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create intents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS intents (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            embedding BLOB,
            examples TEXT
        )
    ''')
    
    # Create queries table (for logging)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            intent TEXT,
            confidence REAL,
            route TEXT,
            latency_ms REAL,
            cost_usd REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Database initialized at", DATABASE_PATH)

if __name__ == "__main__":
    init_database()
    