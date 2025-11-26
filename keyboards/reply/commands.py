from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard():
    """Основная клавиатура с командами"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    keyboard.add(
        KeyboardButton('/movie_search'),
        KeyboardButton('/movie_by_rating'),
        KeyboardButton('/low_budget_movie'),
        KeyboardButton('/high_budget_movie'),
        KeyboardButton('/history'),
        KeyboardButton('/help')
    )

    return keyboard
