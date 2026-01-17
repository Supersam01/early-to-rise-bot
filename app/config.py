import os
from datetime import datetime

BOT_TOKEN = "8397097729:AAE7eextZCH1DuqMjyNjxhPy2t1OqxO7HJo"
ADMIN_USERNAME = "@early_to_rise"

DB_PATH = "app/early_to_rise.db"

# Stock limit per item
MAX_STOCK_PER_ITEM = 10

# Packaging fee
PACKAGING_FEE_PER_ITEM = 200

# Delivery rules
HOSTEL_PRIORITY = [
    "Dorcas", "Deborah", "Lydia", "Mary", "Daniel",
    "Joseph", "Paul", "Peter", "Esther", "John"
]

DELIVERY_WINDOW_MINUTES = 10  # 10-minute window

# Bot active period
START_DATE = datetime(2026, 1, 18)
END_DATE = datetime(2026, 2, 28)

# Language
LANGUAGE = "EN"
