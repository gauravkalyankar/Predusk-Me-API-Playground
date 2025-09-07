import sqlite3

DATABASE = 'profile.db'

def init_db():
    """Initializes the database using the schema.sql file."""
    with sqlite3.connect(DATABASE) as con:
        with open('schema.sql', 'r') as f:
            con.executescript(f.read())
        print("Initialized the database.")

if __name__ == '__main__':
    init_db()
