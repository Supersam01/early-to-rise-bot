import sqlite3

DB_PATH = "early_to_rise.db"

def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        state TEXT,
        cart_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        admin_id INTEGER PRIMARY KEY,
        name TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price INTEGER,
        profit INTEGER,
        category TEXT,
        combo_type TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock (
        item_id INTEGER PRIMARY KEY,
        quantity INTEGER
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS carts (
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cart_id INTEGER,
        item_id INTEGER,
        combo_type TEXT,
        item_type TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        cart_id INTEGER,
        hostel TEXT,
        email TEXT,
        status TEXT,
        order_code TEXT,
        total INTEGER,
        packaging_fee INTEGER,
        pickup_start DATETIME,
        pickup_end DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        item_id INTEGER,
        combo_type TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        admin_id INTEGER,
        status TEXT,
        confirmed_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()


def populate_items(conn):
    cursor = conn.cursor()

    items = [
        # Combo B liquids
        ("BLACK COFFEE", 500, 100, "liquid", "B"),
        ("HOT COFFEE", 600, 100, "liquid", "B"),
        ("HOT CHOCOLATE", 600, 100, "liquid", "B"),
        ("COFFEE BANANA SMOOTHIE", 1100, 100, "liquid", "B"),
        ("BANANA PINEY SMOOTHIE", 600, 100, "liquid", "B"),
        ("BANANA MILKSHAKE", 1400, 200, "liquid", "B"),
        ("CHOCOLATE MILKSHAKE", 900, 100, "liquid", "B"),
        ("COFFEE MILKSHAKE", 1400, 200, "liquid", "B"),
        ("OREOS MILKSHAKE", 1400, 200, "liquid", "B"),

        # Combo A liquids
        ("HOT CHOCOLATE WITH WHIPPED CREAM", 2200, 200, "liquid", "A"),
        ("VANILLA MILKSHAKE", 2200, 200, "liquid", "A"),
        ("PINEAPPLE PARFAIT", 2800, 300, "liquid", "A"),
        ("APPLE PARFAIT", 2800, 300, "liquid", "A"),
        ("MIXED FRUITS PARFAIT", 3300, 300, "liquid", "A"),
        ("COOKIES AND CREAM PARFAIT", 3300, 300, "liquid", "A"),

        # Combo B solids
        ("PANCAKES, EGGS, SYRUP AND SAUSAGE", 1100, 100, "solid", "B"),
        ("PANCAKES, EGGS, SYRUP AND CHICKEN", 2200, 200, "solid", "B"),
        ("WAFFLES, EGGS, SYRUP AND CHICKEN", 2800, 300, "solid", "B"),
        ("WAFFLES, EGGS, SAUSAGE, SYRUP", 1300, 200, "solid", "B"),
        ("FRENCH TOAST", 1700, 200, "solid", "B"),
        ("EGG & CHICKEN SANDWICH", 1400, 200, "solid", "B"),
        ("SUYA STIR FRY SPAGHETTI", 1400, 200, "solid", "B"),
        ("WHITE SPAGHETTI & SAUCE", 900, 100, "solid", "B"),
        ("GLAZED DONUT", 1400, 200, "solid", "B"),

        # Combo A solids
        ("PANCAKES, EGG, AND SYRUP", 700, 100, "solid", "A"),
        ("BANANA PANCAKES", 500, 100, "solid", "A"),
        ("PLAIN PANCAKE", 300, 100, "solid", "A"),
        ("WAFFLES, EGGS AND SYRUP", 800, 100, "solid", "A"),
        ("PLAIN WAFFLE", 400, 100, "solid", "A"),
        ("EGG TOAST", 400, 100, "solid", "A"),
        ("YAMARITA & EGG SAUCE", 1800, 200, "solid", "A"),
        ("EGG SAUCE", 500, 100, "solid", "A"),
        ("CHICKEN SAUCE SANDWICH", 500, 100, "solid", "A"),
        ("PLAIN DONUT", 600, 100, "solid", "A"),
        ("DONUT WAFFLE", 900, 100, "solid", "A"),
        ("SAUSAGE ROLL", 600, 100, "solid", "A"),
        ("EGG ROLL", 700, 100, "solid", "A"),
    ]

    cursor.executemany("""
    INSERT INTO items (name, price, profit, category, combo_type)
    VALUES (?, ?, ?, ?, ?)
    """, items)

    conn.commit()


def initialize_stock(conn):
    cursor = conn.cursor()

    cursor.execute("SELECT item_id FROM items")
    item_ids = cursor.fetchall()

    for item_id in item_ids:
        cursor.execute("""
        INSERT OR REPLACE INTO stock (item_id, quantity)
        VALUES (?, 10)
        """, (item_id[0],))

    conn.commit()


def add_admin(conn):
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO admins (admin_id, name)
    VALUES (?, ?)
    """, (8251843110, "@early_to_rise"))

    conn.commit()


def main():
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)
    populate_items(conn)
    initialize_stock(conn)
    add_admin(conn)
    conn.close()

if __name__ == "__main__":
    main()
