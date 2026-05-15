import sqlite3

def get_db():
    conn = sqlite3.connect("balance.db")
    conn.row_factory = sqlite3.Row
    return conn
def init_db():

    db=get_db()

    db.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        option_a TEXT,
        option_b TEXT,
        vote_a INTEGER DEFAULT 0,
        vote_b INTEGER DEFAULT 0,
        user_id INTEGER
    )
    """)
    
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT,
        post_id INTEGER,
        user_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )          
    """)
    db.commit()
    db.close()