import json
from loguru import logger
from loader import bot
from telebot.types import Message
from database.models import User, SearchHistory
from services.api import kinopoisk_api
from services.message import MessageFormatter
from utils.validators import validate_limit_input
from utils.shared import user_states_manager, send_movie_with_poster, send_and_delete_search_message


@bot.message_handler(commands=['low_budget_movie', 'high_budget_movie'])
def handle_budget_movie_search(message: Message):
    """Обработчик команды поиска фильмов по бюджету"""
    try:
        User.get_or_create(
            user_id=message.from_user.id,
            defaults={
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name
            }
        )

        is_low_budget = message.text == '/low_budget_movie'
        budget_type = "низким" if is_low_budget else "высоким"

        user_states_manager.set_state_with_data(
            message.from_user.id,
            'budget_movie',
            'waiting_genre',
            {
                'is_low_budget': is_low_budget,
                'budget_type': budget_type
            }
        )

        bot.send_message(message.chat.id,
            f"💰 <b>Поиск фильмов с {budget_type} бюджетом</b>\n\n"
            f"🎭 <b>Выберите жанр:</b>\nПример: <code>комедия</code>, <code>драма</code>", parse_mode='HTML')

    except Exception as e:
        logger.error(f"Error in handle_budget_movie_search: {e}")
        bot.reply_to(message, "❌ Произошла ошибка при запуске поиска")


@bot.message_handler(func=lambda message: user_states_manager.get_state(message.from_user.id, 'budget_movie') == 'waiting_genre')
def handle_budget_genre(message: Message):
    """Обрабатывает введённый жанр"""
    user_id = message.from_user.id

    genre = message.text.strip() if message.text.strip() else None

    user_states_manager.set_state(user_id, 'budget_movie', 'waiting_limit')
    user_states_manager.update_state(user_id, 'budget_movie', {'genre': genre})

    bot.send_message(message.chat.id, "📊 <b>Сколько результатов показать?</b>\n\nВведите число от 1 до 20:", parse_mode='HTML')


@bot.message_handler(func=lambda message: user_states_manager.get_state(message.from_user.id, 'budget_movie') == 'waiting_limit')
def handle_budget_limit(message: Message):
    """Обрабатывает количество результатов"""
    user_id = message.from_user.id
    user = User.get(User.user_id == user_id)

    user_state = user_states_manager.get_state_data(user_id, 'budget_movie')
    is_low_budget = user_state.get('is_low_budget', True)
    budget_type = user_state.get('budget_type', 'низким')
    genre = user_state.get('genre')

    if message.text.strip() == '':
        limit = 10
    else:
        is_valid, limit = validate_limit_input(message.text)
        if not is_valid:
            bot.send_message(message.chat.id,"❌ Неверное количество. Введите число от 1 до 20:")
            return

    send_and_delete_search_message(bot, message.chat.id)

    if is_low_budget:
        search_results = kinopoisk_api.get_low_budget_movies(genre=genre, limit=limit)
    else:
        search_results = kinopoisk_api.get_high_budget_movies(genre=genre, limit=limit)

    all_movies = search_results['docs']
    movies = MessageFormatter.filter_valid_movies(all_movies)

    query_text = f"бюджет: {budget_type}"
    if genre:
        query_text += f", жанр: {genre}"

    for movie in movies[:3]:
        SearchHistory.create(
            user=user,
            command='low_budget_movie' if is_low_budget else 'high_budget_movie',
            query=query_text,
            movie_data=json.dumps(movie, ensure_ascii=False)
        )

    summary_text = MessageFormatter.format_search_results(movies, "фильмов")
    bot.send_message(message.chat.id, summary_text, parse_mode='HTML')

    if movies:
        first_movie = movies[0]
        first_movie_details = kinopoisk_api.get_movie_details(first_movie['id'])
        send_movie_with_poster(bot, message.chat.id, first_movie, first_movie_details)

    user_states_manager.clear_state(user_id, 'budget_movie')
