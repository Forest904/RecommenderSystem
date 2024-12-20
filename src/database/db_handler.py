import sqlite3
from flask import Flask, g

DATABASE = "app.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def init_db(app):
    with app.app_context():
        db = get_db()
        try:
            with open("schema.sql", "r") as f:
                db.executescript(f.read())
            db.commit()
        except FileNotFoundError:
            print("Error: 'schema.sql' file not found.")
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")


def close_db_connection(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

