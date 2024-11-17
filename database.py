import sqlite3 as db

# Initialize the SQLite database
def init_db():
    conn = db.connect('backend_data.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT,
        value TEXT,
        created_time TEXT,
        updated_time TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Fetch all records from the database
def fetch_records():
    conn = db.connect('backend_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT key, value, created_time, updated_time FROM records')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Perform database operations (insert, update, delete)
def backend(action, key, value=None):
    conn = db.connect('backend_data.db')
    cursor = conn.cursor()
    if action == "insert":
        cursor.execute('''
        INSERT INTO records (key, value, created_time, updated_time)
        VALUES (?, ?, datetime('now'), NULL)
        ''', (key, value))
    elif action == "update":
        cursor.execute('''
        UPDATE records
        SET value = ?, updated_time = datetime('now')
        WHERE key = ?
        ''', (value, key))
    elif action == "delete":
        cursor.execute('''
        DELETE FROM records
        WHERE key = ?
        ''', (key,))
    conn.commit()
    conn.close()
