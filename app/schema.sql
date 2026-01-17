CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    ref_code TEXT UNIQUE,
    hostel TEXT,
    items TEXT, -- JSON string
    total_price INTEGER,
    status TEXT DEFAULT 'PENDING',
    delivery_slot TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stock (
    item_name TEXT PRIMARY KEY,
    quantity INTEGER,
    last_reset_date TEXT
);

