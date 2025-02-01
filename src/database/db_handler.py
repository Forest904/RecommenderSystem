import sqlite3
from flask import Flask, g

DATABASE = "app.db"

def get_db():
    if "db" not in g:
        #print("[DEBUG] Connecting to the database...")  # Debug log
        g.db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)  # Allows multithreading  g.db.row_factory = sqlite3.Row
        g.db.row_factory = sqlite3.Row
        #print("[DEBUG] Database connection established.")  # Debug log
    return g.db


def init_db(app):
    with app.app_context():
        db = get_db()
        try:
            #print("[DEBUG] Attempting to initialize the database schema...")  # Debug log
            with open("src\database\schema.sql", "r") as f:
                db.executescript(f.read())
            db.commit()
            #print("[DEBUG] Database schema successfully applied.")  # Debug log
        except FileNotFoundError:
            print("[ERROR] 'schema.sql' file not found.")
        except sqlite3.DatabaseError as e:
            print(f"[ERROR] Database error during initialization: {e}")


def close_db_connection(exception):
    db = g.pop("db", None)
    if db is not None:
        print("[DEBUG] Closing the database connection...")  # Debug log
        db.close()
        print("[DEBUG] Database connection closed.")  # Debug log
