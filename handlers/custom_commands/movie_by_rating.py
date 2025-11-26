import json
from loguru import logger
from loader import bot
from telebot.types import Message
from database.models import User, SearchHistory
from services.api import kinopoisk_api
from services.message import MessageFormatter
from utils.shared import user_states_manager, send_movie_with_poster, send_and_delete_search_message
from utils.validators import validate_rating_input, validate_limit_input


@bot.message_handler(commands=['movie_by_rating'])
def handle_movie_by_rating(message: Message):
    """Обработчик команды поиска фильмов по рейтингу"""
    try:
        User.get_or_create(
            user_id=message.from_user.id,
            defaults={
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name
            }
        )

        user_states_manager.set_state(message.from_user.id, 'movie_by_rating', 'waiting_rating_range')

        bot.send_message(message.chat.id,
            "⭐ <b>Поиск фильмов по рейтингу</b>\n\n"
            "Введите диапазон рейтинга:\n"
            "Пример: <code>7-10</code> или <code>8.5-9.5</code>\n"
            "<i>• минимальный рейтинг: 0</i>\n"
            "<i>• максимальный рейтинг: 10</i>",
            parse_mode='HTML')

    except Exception as e:
        logger.error(f"Error in handle_movie_by_rating: {e}")
        bot.reply_to(message, "❌ Произошла ошибка при запуске поиска")


@bot.message_handler(func=lambda message: user_states_manager.get_state(message.from_user.id, 'movie_by_rating') == 'waiting_rating_range')
def handle_rating_range(message: Message):
    """Обработка введенного диапазона рейтинга"""
    user_id = message.from_user.id

    if message.text.strip() == '':
        min_rating, max_rating = 7.0, 10.0
    else:
        is_valid, min_rating, max_rating = validate_rating_input(message.text)
        if not is_valid:
            bot.send_message(message.chat.id, "❌ Неверный формат диапазона")
            return

    user_states_manager.set_state(user_id, 'movie_by_rating', 'waiting_genre')
    user_states_manager.update_state(user_id, 'movie_by_rating', {'step': 'waiting_genre', 'min_rating': min_rating, 'max_rating': max_rating})

    bot.send_message(message.chat.id, "🎭 <b>Введите жанр</b>\n\nПример: <code>комедия</code>, <code>драма</code>", parse_mode='HTML')


@bot.message_handler(func=lambda message: user_states_manager.get_state(message.from_user.id, 'movie_by_rating') == 'waiting_genre')
def handle_genre_input(message: Message):
    """Обработка введенного жанра"""
    user_id = message.from_user.id
    genre = message.text.strip() if message.text.strip() else None

    user_states_manager.set_state(user_id, 'movie_by_rating', 'waiting_limit')
    user_states_manager.update_state(user_id, 'movie_by_rating', {'step': 'waiting_limit', 'genre': genre})

    bot.send_message(message.chat.id, "📊 <b>Сколько результатов показать?</b>\n\nВведите число от 1 до 20:", parse_mode='HTML')


@bot.message_handler(func=lambda message: user_states_manager.get_state(message.from_user.id, 'movie_by_rating') == 'waiting_limit')
def handle_rating_limit(message: Message):
    """Обработка количества результатов для поиска по рейтингу"""
    user_id = message.from_user.id
    user = User.get(User.user_id == user_id)
    user_state = user_states_manager.get_state_data(user_id, 'movie_by_rating')

    min_rating = user_state.get('min_rating', 7.0)
    max_rating = user_state.get('max_rating', 10.0)
    genre = user_state.get('genre')

    if message.text.strip() == '':
        limit = 10
    else:
        is_valid, limit = validate_limit_input(message.text)
        if not is_valid:
            bot.send_message(message.chat.id, "❌ Неверное количество. Введите число от 1 до 20:")
            return

    send_and_delete_search_message(bot, message.chat.id)
    search_results = kinopoisk_api.get_movies_by_rating(min_rating=min_rating, max_rating=max_rating, genre=genre, limit=limit)
    all_movies = search_results['docs']
    movies = MessageFormatter.filter_valid_movies(all_movies)

    query_text = f"рейтинг {min_rating}-{max_rating}"
    if genre:
        query_text += f", жанр: {genre}"

    for movie in movies[:3]:
        SearchHistory.create(
            user=user,
            command='movie_by_rating',
            query=query_text,
            movie_data=json.dumps(movie, ensure_ascii=False)
        )

    summary_text = MessageFormatter.format_search_results(movies, "фильмов")
    bot.send_message(message.chat.id, summary_text, parse_mode='HTML')

    first_movie = movies[0]
    first_movie_details = kinopoisk_api.get_movie_details(first_movie['id'])
    send_movie_with_poster(bot, message.chat.id, first_movie, first_movie_details)

    user_states_manager.clear_state(user_id, 'movie_by_rating')
