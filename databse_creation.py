import sqlite3

def initialize_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('innovative_ideas.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            region TEXT NOT NULL,
            password TEXT NOT NULL
        );
    ''')

    # Create ideas table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            votes INTEGER DEFAULT 0,
            approved INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    ''')

    # Create votes table
    cursor.execute('''
        CREATE TABLE votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            idea_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (idea_id) REFERENCES ideas (id),
            UNIQUE(user_id, idea_id) -- ensures one vote per user per idea
        );

    ''')

    print("Database initialized successfully.")

    # Commit changes and close the connection
    conn.commit()
    conn.close()

# Run the function to initialize the database
if __name__ == '__main__':
    initialize_database()
