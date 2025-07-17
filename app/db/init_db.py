import sqlite3

conn = sqlite3.connect("LADOC.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,     
    password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    username TEXT,
    password TEXT NOT NULL,
    site TEXT,
    notes TEXT,
    folder_path TEXT, -- e.g. "Work/Email"
    password_expiry DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users_folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    parent_id INTEGER,
    FOREIGN KEY (parent_id) REFERENCES users_folders(id)
);
""")

conn.commit()
conn.close()

print("Updated database schema created successfully.")
