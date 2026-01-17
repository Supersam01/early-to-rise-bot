import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "8397097729:AAE7eextZCH1DuqMjyNjxhPy2t1OqxO7HJo")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "@early_to_rise")

DB_PATH = os.getenv("DB_PATH", "app/early_to_rise.db")

DELIVERY_TIME_WINDOW_MINUTES = 10
