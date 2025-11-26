import json
from loguru import logger
from loader import bot
from telebot.types import Message
from database.models import User, SearchHistory
from services.api import kinopoisk_api
from services.message import MessageFormatter
from utils.shared import user_states_manager, send_movie_with_poster, send_and_delete_search_message
from utils.validators import validate_search_query, validate_limit_input


@bot.message_handler(commands=['movie_search'])
def handle_movie_search(message: Message):
    """Обработчик команды поиска фильма"""
    try:
        User.get_or_create(
            user_id=message.from_user.id,
            defaults={
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name
            }
        )

        user_states_manager.set_state(message.from_user.id, 'movie_search', 'waiting_query')

        bot.send_message(message.chat.id, "🔍 <b>Поиск по названию</b>\n\nВведите название фильма или сериала:", parse_mode='HTML')

    except Exception as e:
        logger.error(f"Error in handle_movie_search: {e}")
        bot.reply_to(message, "❌ Произошла ошибка при запуске поиска")


@bot.message_handler(func=lambda message: user_states_manager.get_state(message.from_user.id, 'movie_search') == 'waiting_query')
def handle_movie_query(message: Message):
    """Обрабатывает введённое название фильма"""
    user_id = message.from_user.id

    if not validate_search_query(message.text):
        bot.send_message(message.chat.id, "❌ Неверный запрос. Название должно содержать от 2 до 100 символов.")
        return

    user_states_manager.set_state(user_id, 'movie_search', 'waiting_limit')
    user_states_manager.update_state(user_id, 'movie_search', {'query': message.text})

    bot.send_message(message.chat.id, "📊 <b>Сколько результатов показать?</b>\n\nВведите число от 1 до 20 :", parse_mode='HTML')


@bot.message_handler(func=lambda message: user_states_manager.get_state(message.from_user.id, 'movie_search') == 'waiting_limit')
def handle_movie_limit(message: Message):
    """Обрабатывает количество результатов"""
    user_id = message.from_user.id
    user = User.get(User.user_id == user_id)
    user_state = user_states_manager.get_state_data(user_id, 'movie_search')
    query = user_state.get('query')

    if not query:
        bot.send_message(message.chat.id, "❌ Ошибка. Запрос не найден")
        user_states_manager.clear_state(user_id, 'movie_search')
        return

    if message.text.strip() == '':
        limit = 10
    else:
        is_valid, limit = validate_limit_input(message.text)
        if not is_valid:
            bot.send_message(message.chat.id, "❌ Неверное количество. Введите число от 1 до 20:")
            return

    send_and_delete_search_message(bot, message.chat.id)
    search_results = kinopoisk_api.search_movie(query, limit=limit)
    all_movies = search_results['docs']
    movies = MessageFormatter.filter_valid_movies(all_movies)

    for movie in movies[:3]:
        SearchHistory.create(
            user=user,
            command='movie_search',
            query=query,
            movie_data=json.dumps(movie, ensure_ascii=False)
        )

    if len(movies) == 1:
        movie = movies[0]
        movie_details = kinopoisk_api.get_movie_details(movie['id'])
        send_movie_with_poster(bot, message.chat.id, movie, movie_details)
    else:
        summary_text = MessageFormatter.format_search_results(movies, "фильмов")
        bot.send_message(message.chat.id, summary_text, parse_mode='HTML')

        first_movie = movies[0]
        first_movie_details = kinopoisk_api.get_movie_details(first_movie['id'])
        send_movie_with_poster(bot, message.chat.id, first_movie, first_movie_details)

    user_states_manager.clear_state(user_id, 'movie_search')
