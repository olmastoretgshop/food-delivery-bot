import sqlite3

# Initialize the database
def init_db():
    conn = sqlite3.connect('food_delivery_bot.db')
    cursor = conn.cursor()

    # Create clients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            username TEXT,
            name TEXT,
            phone_number TEXT,
            location TEXT  -- Add location column
        )
    ''')

    # Create menu table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            price REAL,
            image_path TEXT
        )
    ''')

    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            items TEXT,  -- JSON string of cart items
            total_cost REAL,
            status TEXT,  -- e.g., "ordered", "delivered", "cancelled"
            location TEXT,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    ''')

    conn.commit()
    conn.close()

# Helper function to execute queries
def execute_query(query, params=(), fetch=False):
    conn = sqlite3.connect('food_delivery_bot.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch:
        result = cursor.fetchall()
    else:
        result = None
    conn.commit()
    conn.close()
    return result