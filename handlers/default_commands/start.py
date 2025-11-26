from keyboards.reply.commands import main_keyboard
from loader import bot
from database.models import User
from loguru import logger


@bot.message_handler(commands=['start', 'hello_world'])
def start_and_hello_world_handle(message):
    try:
        User.get_or_create(
            user_id=message.from_user.id,
            defaults={
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name
            }
        )

        welcome_text = (
            "<b>Добро пожаловать 🤗</b>\n\n"
            "Бот для поиска фильмов и сериалов 🎞️\n"
            "Помогу вам найти всю необходимую информацию 🗒️\n\n"
            "<b>Доступные команды для поиска:</b>\n"
            "<b>/movie_search</b> - по названию\n"
            "<b>/movie_by_rating</b> - по рейтингу\n"
            "<b>/low_budget_movie</b> - с низким бюджетом\n"
            "<b>/high_budget_movie</b> - с высоким бюджетом\n"
            "<b>/history</b> - история ваших запросов\n\n"
            "Подробная справка по командам - <b>/help</b>\n\n"
            "<i>Вы также можете выбирать нужную команду в меню ниже</i> 👇"
        )

        bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard(), parse_mode='HTML')

    except Exception as e:
        logger.error(f"Error in start_and_hello_world_handle: {e}")
        bot.reply_to(message, "❌ Произошла ошибка при запуске бота")
