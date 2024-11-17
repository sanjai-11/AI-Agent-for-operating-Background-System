import psycopg2
import os
from datetime import datetime
from psycopg2 import IntegrityError
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL not set in environment variables")
        self.connection = psycopg2.connect(db_url)
        self.cursor = self.connection.cursor()
        self.create_default_table()

    def create_default_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id SERIAL PRIMARY KEY,
            key TEXT UNIQUE,
            value TEXT,
            created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_time TIMESTAMP
        )
        ''')
        self.connection.commit()

    def fetch_records(self):
        self.cursor.execute('SELECT key, value, created_time, updated_time FROM records')
        return self.cursor.fetchall()

    def backend(self, action, key, value=None):
        try:
            if action == "insert":
                if key is None or value is None:
                    print("Error: Key and value cannot be null for insert operation.")
                else:
                    self.cursor.execute('''
                    INSERT INTO records (key, value, created_time, updated_time)
                    VALUES (%s, %s, CURRENT_TIMESTAMP, NULL)
                    ''', (key, value))

            elif action == "update":
                self.cursor.execute('''
                UPDATE records
                SET value = %s, updated_time = CURRENT_TIMESTAMP
                WHERE key = %s
                ''', (value, key))

            elif action == "delete":
                if key is None and value is None:
                    self.cursor.execute('''
                    DELETE FROM records
                    WHERE key IS NULL AND value IS NULL
                    ''')
                elif key and value:
                    self.cursor.execute('''
                    DELETE FROM records
                    WHERE key = %s AND value = %s
                    ''', (key, value))
                elif key:
                    self.cursor.execute('''
                    UPDATE records
                    SET key = NULL, updated_time = CURRENT_TIMESTAMP
                    WHERE key = %s
                    ''', (key,))
                elif value:
                    self.cursor.execute('''
                    UPDATE records
                    SET value = NULL, updated_time = CURRENT_TIMESTAMP
                    WHERE value = %s
                    ''', (value,))

            self.connection.commit()

        except IntegrityError as e:
            print(f"IntegrityError: {e}")
            self.connection.rollback()

    def __del__(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()

db_manager = DatabaseManager()            
