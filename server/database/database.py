from pathlib import Path
import sqlite3

class Database:
    def __init__(self):
        # Path of the database file (attention that the name of database file is fixed)
        self.db_path = Path(__file__).parent / "database.db"
        # Check whether the database file exists
        db_exists = self.db_path.is_file()
        # Connect to the database (database file will be created if it does not exist)
        self.connection = sqlite3.connect(self.db_path)
        # Get the cursor of the database
        self.cursor = self.connection.cursor()
        # If the database file was newly created, initialize it
        if not db_exists:
            self._initialize_database()

    def _initialize_database(self):
        # Create table of notebooks
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notebooks (
                id INTEGER PRIMARY KEY,
                notebook_name TEXT NOT NULL UNIQUE,
                notebook_path TEXT NOT NULL UNIQUE,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Create table of notes, notebook_id is a foreign key
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL UNIQUE,
                file_path TEXT NOT NULL UNIQUE,
                notebook_id INTEGER NOT NULL,
                created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (notebook_id) REFERENCES notebooks (id) ON DELETE CASCADE
            )
        ''')
        # Create table of tags
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY,
                tag_name TEXT NOT NULL UNIQUE
            ) 
        ''')
        # Create table of relation among notes and their tags
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS note_tags (
                note_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (note_id, tag_id),
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            )
        ''')
        # Create indices
        self.cursor.execute("CREATE INDEX IF NOT EXISTS notebook_name_idx ON notebooks (notebook_name)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS title_idx ON notes (title)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS tag_name_idx ON tags (tag_name)")
        # Commit transaction
        self.connection.commit()

