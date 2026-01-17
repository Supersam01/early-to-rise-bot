import sqlite3
from sqlite3 import Connection
from typing import List, Optional
from .models import MenuItem, CartItem, Order
from .config import DB_PATH


class Database:
    def __init__(self):
        self.conn: Connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        with open("app/schema.sql", "r") as f:
            self.conn.executescript(f.read())
        self.conn.commit()

    def add_menu_item(self, item: MenuItem):
        self.conn.execute(
            "INSERT INTO menu (name, price, profit, category, stock) VALUES (?, ?, ?, ?, ?)",
            (item.name, item.price, item.profit, item.category, item.stock)
        )
        self.conn.commit()

    def get_menu(self) -> List[MenuItem]:
        rows = self.conn.execute("SELECT * FROM menu").fetchall()
        return [MenuItem(**row) for row in map(dict, rows)]

    def get_menu_item(self, item_id: int) -> Optional[MenuItem]:
        row = self.conn.execute("SELECT * FROM menu WHERE id = ?", (item_id,)).fetchone()
        if not row:
            return None
        return MenuItem(**dict(row))

    def update_stock(self, item_id: int, quantity: int):
        self.conn.execute(
            "UPDATE menu SET stock = stock - ? WHERE id = ?",
            (quantity, item_id)
        )
        self.conn.commit()

    def create_order(self, order: Order) -> int:
        cursor = self.conn.execute(
            "INSERT INTO orders (user_id, username, hostel, combo_type, packaging_fee, total_amount, status, time_slot, reference_code) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                order.user_id,
                order.username,
                order.hostel,
                order.combo_type,
                order.packaging_fee,
                order.total_amount,
                order.status,
                order.time_slot,
                order.reference_code
            )
        )
        self.conn.commit()
        return cursor.lastrowid

    def add_cart_item(self, order_id: int, cart_item: CartItem):
        self.conn.execute(
            "INSERT INTO cart_items (order_id, menu_item_id, quantity, combo_type) VALUES (?, ?, ?, ?)",
            (order_id, cart_item.menu_item_id, cart_item.quantity, cart_item.combo_type)
        )
        self.conn.commit()

    def get_pending_orders(self) -> List[Order]:
        rows = self.conn.execute("SELECT * FROM orders WHERE status = 'pending'").fetchall()
        return [Order(**dict(row)) for row in map(dict, rows)]

    def update_order_status(self, order_id: int, status: str):
        self.conn.execute(
            "UPDATE orders SET status = ? WHERE id = ?",
            (status, order_id)
        )
        self.conn.commit()
