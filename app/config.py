import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8397097729:AAE7eextZCH1DuqMjyNjxhPy2t1OqxO7HJo")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "8251843110"))

DB_PATH = os.getenv("DB_PATH", "app/early_to_rise.db")

PACKAGING_FEE_PER_ITEM = 200
DELIVERY_WINDOW_MINUTES = 10

HOSTEL_PRIORITY = [
    "Dorcas", "Deborah", "Lydia", "Mary",
    "Daniel", "Joseph", "Paul", "Peter",
    "Esther", "John"
]
