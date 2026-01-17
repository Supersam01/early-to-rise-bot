import sqlite3
import json
from datetime import datetime

DB_PATH = "early_to_rise.db"
DEFAULT_STOCK = 10

def init_db():
    """Initialize the database tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Orders Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        ref_code TEXT UNIQUE,
        hostel TEXT,
        items TEXT, -- Stored as JSON string
        total_price INTEGER,
        status TEXT DEFAULT 'PENDING', -- PENDING, PAID
        delivery_slot TEXT DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Stock Table (Tracks daily limits)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock (
        item_name TEXT PRIMARY KEY,
        quantity INTEGER,
        last_reset_date TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

def _get_today_str():
    return datetime.now().strftime("%Y-%m-%d")

def check_stock(item_name):
    """
    Checks if an item is in stock for the current day.
    Resets stock to 10 if it's a new day.
    Returns True if stock > 0.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    today = _get_today_str()
    
    cursor.execute("SELECT quantity, last_reset_date FROM stock WHERE item_name = ?", (item_name,))
    row = cursor.fetchone()
    
    current_qty = 0
    
    if row is None:
        # Item never tracked, insert default
        cursor.execute("INSERT INTO stock (item_name, quantity, last_reset_date) VALUES (?, ?, ?)", 
                       (item_name, DEFAULT_STOCK, today))
        current_qty = DEFAULT_STOCK
        conn.commit()
    else:
        qty, last_date = row
        if last_date != today:
            # New day, reset stock
            cursor.execute("UPDATE stock SET quantity = ?, last_reset_date = ? WHERE item_name = ?", 
                           (DEFAULT_STOCK, today, item_name))
            current_qty = DEFAULT_STOCK
            conn.commit()
        else:
            current_qty = qty
            
    conn.close()
    return current_qty > 0

def reduce_stock(item_list):
    """
    Reduces stock for a list of items by 1.
    Call this ONLY when order is confirmed/placed.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today = _get_today_str()
    
    for item_name in item_list:
        # Ensure record exists and is fresh before reducing (reuse check logic slightly)
        cursor.execute("SELECT quantity, last_reset_date FROM stock WHERE item_name = ?", (item_name,))
        row = cursor.fetchone()
        
        if row is None:
            cursor.execute("INSERT INTO stock VALUES (?, ?, ?)", (item_name, DEFAULT_STOCK - 1, today))
        else:
            qty, last_date = row
            if last_date != today:
                # Reset then reduce
                new_qty = DEFAULT_STOCK - 1
                cursor.execute("UPDATE stock SET quantity = ?, last_reset_date = ? WHERE item_name = ?", 
                               (new_qty, today, item_name))
            else:
                # Just reduce
                new_qty = max(0, qty - 1)
                cursor.execute("UPDATE stock SET quantity = ? WHERE item_name = ?", (new_qty, item_name))
                
    conn.commit()
    conn.close()

def save_order(user_id, ref_code, hostel, items_data, total_price):
    """Saves a new order to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # items_data is a list of dicts, convert to JSON string
    items_json = json.dumps(items_data)
    
    cursor.execute('''
        INSERT INTO orders (user_id, ref_code, hostel, items, total_price)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, ref_code, hostel, items_json, total_price))
    
    conn.commit()
    conn.close()

def get_order(ref_code):
    """Retrieve order details by reference code."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE ref_code = ?", (ref_code,))
    row = cursor.fetchone()
    conn.close()
    return row

def update_order_paid(ref_code, delivery_slot):
    """Marks order as PAID and assigns the delivery slot."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = 'PAID', delivery_slot = ? WHERE ref_code = ?", 
                   (delivery_slot, ref_code))
    conn.commit()
    conn.close()

def get_paid_count_for_hostel(hostel):
    """Counts how many PAID orders exist for a specific hostel today."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # We filter by created_at to ensure we only count TODAY's orders for the time slot logic
    # SQLite 'date' function extracts YYYY-MM-DD
    cursor.execute('''
        SELECT COUNT(*) FROM orders 
        WHERE hostel = ? 
        AND status = 'PAID' 
        AND date(created_at) = date('now')
    ''', (hostel,))
    
    count = cursor.fetchone()[0]
    conn.close()
    return count
