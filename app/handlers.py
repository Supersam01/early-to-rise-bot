from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters, Application
)

from .config import BOT_TOKEN, ADMIN_USER_ID, HOSTEL_PRIORITY, DELIVERY_WINDOW_MINUTES, PACKAGING_FEE_PER_ITEM
from .database import Database
from .utils import generate_reference_code, calculate_packaging_fee, validate_combo

db = Database()

# STATES
START, CHOOSE_HOSTEL, MENU, CART, PAYMENT = range(5)

# MENU ITEMS (Hardcoded)
MENU = [
    # Combo A Liquids
    {"id": 1, "name": "HOT CHOCOLATE WITH WHIPPED CREAM", "price": 2200, "profit": 200, "category": "liquid", "combo": "A"},
    {"id": 2, "name": "VANILLA MILKSHAKE", "price": 2200, "profit": 200, "category": "liquid", "combo": "A"},
    {"id": 3, "name": "PINEAPPLE PARFAIT", "price": 2800, "profit": 300, "category": "liquid", "combo": "A"},
    {"id": 4, "name": "APPLE PARFAIT", "price": 2800, "profit": 300, "category": "liquid", "combo": "A"},
    {"id": 5, "name": "MIXED FRUITS PARFAIT", "price": 3300, "profit": 300, "category": "liquid", "combo": "A"},
    {"id": 6, "name": "COOKIES AND CREAM PARFAIT", "price": 3300, "profit": 300, "category": "liquid", "combo": "A"},

    # Combo A Solids
    {"id": 7, "name": "PANCAKES, EGG AND SYRUP", "price": 700, "profit": 100, "category": "solid", "combo": "A"},
    {"id": 8, "name": "BANANA PANCAKES", "price": 500, "profit": 100, "category": "solid", "combo": "A"},
    {"id": 9, "name": "PLAIN PANCAKES", "price": 300, "profit": 100, "category": "solid", "combo": "A"},
    {"id": 10, "name": "WAFFLES, EGG AND SYRUP", "price": 800, "profit": 100, "category": "solid", "combo": "A"},
    {"id": 11, "name": "PLAIN WAFFLES", "price": 400, "profit": 100, "category": "solid", "combo": "A"},
    {"id": 12, "name": "EGG TOAST", "price": 400, "profit": 100, "category": "solid", "combo": "A"},
    {"id": 13, "name": "EGG SAUCE", "price": 1800, "profit": 200, "category": "solid", "combo": "A"},
    {"id": 14, "name": "CHICKEN SAUCE SANDWICH", "price": 500, "profit": 100, "category": "solid", "combo": "A"},
    {"id": 15, "name": "PLAIN DONUT", "price": 600, "profit": 100, "category": "solid", "combo": "A"},
    {"id": 16, "name": "DONUT WAFFLES", "price": 900, "profit": 100, "category": "solid", "combo": "A"},
    {"id": 17, "name": "SAUSAGE ROLL", "price": 600, "profit": 100, "category": "solid", "combo": "A"},
    {"id": 18, "name": "EGG ROLL", "price": 700, "profit": 100, "category": "solid", "combo": "A"},

    # Combo B Liquids
    {"id": 19, "name": "BLACK COFFEE", "price": 500, "profit": 100, "category": "liquid", "combo": "B"},
    {"id": 20, "name": "HOT COFFEE", "price": 600, "profit": 100, "category": "liquid", "combo": "B"},
    {"id": 21, "name": "HOT CHOCOLATE", "price": 600, "profit": 100, "category": "liquid", "combo": "B"},
    {"id": 22, "name": "COFFEE BANANA SMOOTHIE", "price": 1100, "profit": 100, "category": "liquid", "combo": "B"},
    {"id": 23, "name": "BANANA PINEY SMOOTHIE", "price": 600, "profit": 100, "category": "liquid", "combo": "B"},
    {"id": 24, "name": "BANANA MILKSHAKE", "price": 1400, "profit": 200, "category": "liquid", "combo": "B"},
    {"id": 25, "name": "CHOCOLATE MILKSHAKE", "price": 900, "profit": 100, "category": "liquid", "combo": "B"},
    {"id": 26, "name": "COFFEE MILKSHAKE", "price": 1400, "profit": 200, "category": "liquid", "combo": "B"},
    {"id": 27, "name": "OREOS MILKSHAKE", "price": 1400, "profit": 200, "category": "liquid", "combo": "B"},

    # Combo B Solids
    {"id": 28, "name": "PANCAKES, EGGS, SYRUP AND SAUSAGE", "price": 1100, "profit": 100, "category": "solid", "combo": "B"},
    {"id": 29, "name": "PANCAKES, EGGS, SYRUP AND CHICKEN", "price": 2200, "profit": 200, "category": "solid", "combo": "B"},
    {"id": 30, "name": "WAFFLES, EGGS, SYRUP AND CHICKEN", "price": 2800, "profit": 300, "category": "solid", "combo": "B"},
    {"id": 31, "name": "WAFFLES, EGGS, SAUSAGE AND SYRUP", "price": 1300, "profit": 200, "category": "solid", "combo": "B"},
    {"id": 32, "name": "FRENCH TOAST", "price": 1700, "profit": 200, "category": "solid", "combo": "B"},
    {"id": 33, "name": "EGG & CHICKEN SANDWICH", "price": 1400, "profit": 200, "category": "solid", "combo": "B"},
    {"id": 34, "name": "SUYA STIR FRY SPAGHETTI", "price": 1400, "profit": 200, "category": "solid", "combo": "B"},
    {"id": 35, "name": "WHITE SPAGHETTI AND SAUCE", "price": 900, "profit": 100, "category": "solid", "combo": "B"},
    {"id": 36, "name": "GLAZED DONUT", "price": 1400, "profit": 200, "category": "solid", "combo": "B"}
]


def start(update: Update, context: CallbackContext):
    now = datetime.now()
    start_date = datetime(2026, 1, 18)
    end_date = datetime(2026, 2, 28)

    if now < start_date or now > end_date:
        update.message.reply_text("Bot is currently inactive.")
        return ConversationHandler.END

    keyboard = [
        [InlineKeyboardButton("Order Combo A", callback_data="combo_A")],
        [InlineKeyboardButton("Order Combo B", callback_data="combo_B")],
        [InlineKeyboardButton("View Cart", callback_data="view_cart")],
    ]
    update.message.reply_text(
        "Welcome to *Early To Rise Breakfast*!\n\nChoose a combo to start ordering.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return START


def combo_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    combo_type = query.data.split("_")[1]
    context.user_data["combo_type"] = combo_type
    context.user_data["cart"] = []
    context.user_data["liquid_count"] = 0
    context.user_data["solid_count"] = 0

    query.edit_message_text(
        f"Combo {combo_type} selected.\nYou must select according to the rules.\n\nCombo A = 1 Liquid + 2 Solids\nCombo B = 1 Liquid + 1 Solid\n\nClick below to view menu.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Show Menu", callback_data="show_menu")],
            [InlineKeyboardButton("View Cart", callback_data="view_cart")],
            [InlineKeyboardButton("Cancel", callback_data="cancel_order")]
        ])
    )
    return MENU


def show_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    combo_type = context.user_data.get("combo_type")

    message = "📋 *MENU*\n\n"

    # show only combo selected items
    for item in MENU:
        if item["combo"] == combo_type:
            message += f"{item['id']}. {item['name']} - ₦{item['price']}\n"

    message += "\nSend the item ID to add to cart.\nExample: `7`"

    query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("View Cart", callback_data="view_cart")],
            [InlineKeyboardButton("Cancel", callback_data="cancel_order")]
        ])
    )
    return MENU


def receive_item_id(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    if not text.isdigit():
        return update.message.reply_text("Send a valid item ID (number).")

    item_id = int(text)
    combo_type = context.user_data.get("combo_type")

    # find item
    item = next((x for x in MENU if x["id"] == item_id and x["combo"] == combo_type), None)
    if not item:
        return update.message.reply_text("Invalid item ID for your combo.")

    # check stock
    stock = db.conn.execute("SELECT stock FROM menu WHERE id = ?", (item_id,)).fetchone()
    if not stock:
        return update.message.reply_text("Item not available.")
    if stock["stock"] <= 0:
        return update.message.reply_text("Item out of stock.")

    # validate combo counts
    liquid_count = context.user_data.get("liquid_count", 0)
    solid_count = context.user_data.get("solid_count", 0)

    if item["category"] == "liquid":
        if liquid_count >= 1:
            return update.message.reply_text("You can only select 1 liquid.")
        context.user_data["liquid_count"] += 1
    else:
        if combo_type == "A" and solid_count >= 2:
            return update.message.reply_text("Combo A allows only 2 solids.")
        if combo_type == "B" and solid_count >= 1:
            return update.message.reply_text("Combo B allows only 1 solid.")
        context.user_data["solid_count"] += 1

    # add to cart
    cart = context.user_data.get("cart", [])
    cart.append(item)
    context.user_data["cart"] = cart

    return update.message.reply_text("Item added to cart.\nSend /cart to view cart.")


def view_cart(update: Update, context: CallbackContext):
    cart = context.user_data.get("cart", [])
    if not cart:
        return update.message.reply_text("Cart is empty.")

    message = "🛒 *Your Cart*\n\n"
    total = 0
    for idx, item in enumerate(cart, start=1):
        message += f"{idx}. {item['name']} - ₦{item['price']}\n"
        total += item["price"]

    packaging_fee = calculate_packaging_fee(len(cart))
    total += packaging_fee

    message += f"\nPackaging Fee: ₦{packaging_fee}\n"
    message += f"Total Payable: ₦{total}"

    update.message.reply_text(
        message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Proceed to Payment", callback_data="proceed_payment")],
            [InlineKeyboardButton("Clear Cart", callback_data="clear_cart")],
            [InlineKeyboardButton("Cancel", callback_data="cancel_order")]
        ])
    )
    return CART


def clear_cart(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    context.user_data["cart"] = []
    context.user_data["liquid_count"] = 0
    context.user_data["solid_count"] = 0
    query.edit_message_text("Cart cleared. Start a new order with /start.")
    return START


def cancel_order(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    context.user_data.clear()
    query.edit_message_text("Order cancelled. Start again with /start.")
    return START


def choose_hostel(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Send your hostel name.\n\nHostels:\n" +
        "\n".join(HOSTEL_PRIORITY)
    )
    return CHOOSE_HOSTEL


def receive_hostel(update: Update, context: CallbackContext):
    hostel = update.message.text.strip()
    if hostel not in HOSTEL_PRIORITY:
        return update.message.reply_text("Invalid hostel. Try again.")

    context.user_data["hostel"] = hostel
    update.message.reply_text("Hostel saved.\nNow go back to /start to order.")
    return START


def assign_time_slot(hostel: str):
    # count orders in hostel today
    today = datetime.now().strftime("%Y-%m-%d")
    rows = db.conn.execute(
        "SELECT COUNT(*) as count FROM orders WHERE hostel = ? AND DATE(created_at) = ?",
        (hostel, today)
    ).fetchone()

    order_count = rows["count"]
    window_index = order_count // 15  # every 15 orders is one window

    start = datetime.strptime("05:30", "%H:%M") + timedelta(minutes=window_index * DELIVERY_WINDOW_MINUTES)
    end = start + timedelta(minutes=DELIVERY_WINDOW_MINUTES)
    return f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}"


def proceed_payment(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    cart = context.user_data.get("cart", [])
    if not cart:
        return query.edit_message_text("Cart is empty.")

    hostel = context.user_data.get("hostel")
    if not hostel:
        return query.edit_message_text("Send your hostel first with /hostel")

    # validate combo completion
    liquid_count = context.user_data.get("liquid_count", 0)
    solid_count = context.user_data.get("solid_count", 0)
    combo_type = context.user_data.get("combo_type")

    if not validate_combo(combo_type, liquid_count, solid_count):
        return query.edit_message_text("Your cart does not match the combo rule. Please fix it.")

    # check stock and reduce
    for item in cart:
        stock = db.conn.execute("SELECT stock FROM menu WHERE id = ?", (item["id"],)).fetchone()
        if stock["stock"] <= 0:
            return query.edit_message_text(f"Item {item['name']} is out of stock.")

    # update stock
    for item in cart:
        db.conn.execute("UPDATE menu SET stock = stock - 1 WHERE id = ?", (item["id"],))
    db.conn.commit()

    # calculate total
    total = sum(i["price"] for i in cart)
    packaging_fee = calculate_packaging_fee(len(cart))
    total += packaging_fee

    # create order
    reference_code = generate_reference_code()
    time_slot = assign_time_slot(hostel)

    user = update.effective_user
    from .models import Order, CartItem
    order = Order(
        id=0,
        user_id=user.id,
        username=user.username,
        hostel=hostel,
        combo_type=combo_type,
        items=[CartItem(menu_item_id=i["id"], quantity=1, combo_type=combo_type) for i in cart],
        packaging_fee=packaging_fee,
        total_amount=total,
        status="pending",
        time_slot=time_slot,
        reference_code=reference_code
    )

    order_id = db.create_order(order)
    for item in order.items:
        db.add_cart_item(order_id, item)

    query.edit_message_text(
        f"Order placed!\nRef: {reference_code}\nTotal: ₦{total}\nTime Slot: {time_slot}\nStatus: Pending payment.\n\nAdmin will confirm payment."
    )

    # notify admin
    context.bot.send_message(
        ADMIN_USER_ID,
        f"New Order Pending\nRef: {reference_code}\nUser: @{user.username}\nHostel: {hostel}\nTotal: ₦{total}\nTime Slot: {time_slot}"
    )

    return PAYMENT


def admin_confirm_payment(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    if not text.startswith("/confirm"):
        return

    _, ref = text.split(" ", 1)
    row = db.conn.execute("SELECT * FROM orders WHERE reference_code = ?", (ref,)).fetchone()
    if not row:
        return update.message.reply_text("Invalid reference code.")

    db.update_order_status(row["id"], "paid")

    context.bot.send_message(
        row["user_id"],
        f"Payment confirmed for order {ref}.\nYour order will be delivered at {row['time_slot']}."
    )
    update.message.reply_text("Payment confirmed.")


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START: [
                CallbackQueryHandler(combo_selection, pattern="^combo_"),
                CallbackQueryHandler(view_cart, pattern="^view_cart$")
            ],
            MENU: [
                CallbackQueryHandler(show_menu, pattern="^show_menu$"),
                CallbackQueryHandler(view_cart, pattern="^view_cart$"),
                CallbackQueryHandler(cancel_order, pattern="^cancel_order$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_item_id)
            ],
            CART: [
                CallbackQueryHandler(proceed_payment, pattern="^proceed_payment$"),
                CallbackQueryHandler(clear_cart, pattern="^clear_cart$"),
                CallbackQueryHandler(cancel_order, pattern="^cancel_order$")
            ],
            CHOOSE_HOSTEL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_hostel)
            ],
            PAYMENT: []
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("hostel", choose_hostel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_confirm_payment))

    app.run_polling()


if __name__ == "__main__":
    main()
