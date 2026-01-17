import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8397097729:AAE7eextZCH1DuqMjyNjxhPy2t1OqxO7HJo")
DB_PATH = os.getenv("DB_PATH", "early_to_rise.db")

ADMIN_ID = 8251843110

HOSTEL_ORDER = [
    "Dorcas",
    "Deborah",
    "Lydia",
    "Mary",
    "Daniel",
    "Joseph",
    "Paul",
    "Peter",
    "Esther",
    "John"
]

# time slots rule
TIME_SLOT_FIRST_15 = ("05:30", "05:40")
TIME_SLOT_LAST_15 = ("07:00", "07:10")
