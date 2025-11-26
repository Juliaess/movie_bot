from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def history_keyboard():
    """Клавиатура для истории"""
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton("📅 За сегодня", callback_data="history_today"),
        InlineKeyboardButton("📆 За неделю", callback_data="history_week"),
        InlineKeyboardButton("🗓️ За все время", callback_data="history_all")
    )

    return keyboard
