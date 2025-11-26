from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def pagination_keyboard(current_page: int, total_pages: int, command: str):
    """Клавиатура для пагинации"""
    keyboard = InlineKeyboardMarkup(row_width=3)

    buttons = []

    if current_page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"{command}_{current_page - 1}"))
    else:
        buttons.append(InlineKeyboardButton("⏺️", callback_data="current_page"))

    buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="current_page"))

    if current_page < total_pages:
        buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"{command}_{current_page + 1}"))
    else:
        buttons.append(InlineKeyboardButton("⏺️", callback_data="current_page"))

    keyboard.add(*buttons)

    if command.startswith('history_'):
        keyboard.add(InlineKeyboardButton("📅 Выбрать другой период", callback_data="history_periods"))

    return keyboard
