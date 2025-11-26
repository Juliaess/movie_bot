import os

BOT_TOKEN = os.getenv('BOT_TOKEN')
API_KEY = os.getenv('API_KEY')

DB_NAME = os.getenv('POSTGRES_DB', 'movie_bot')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')

DEFAULT_COMMANDS = (
        ("start", "Начать работу"),
        ("help", "Помощь по командам"),
        ("movie_search", "Поиск фильма по названию"),
        ("movie_by_rating", "Поиск фильмов по рейтингу"),
        ("low_budget_movie", "Поиск фильмов с низким бюджетом"),
        ("high_budget_movie", "Поиск фильмов с высоким бюджетом"),
        ("history", "История запросов")
)

BASE_URL = "https://api.kinopoisk.dev/v1.4"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

if not API_KEY:
    raise ValueError("API_KEY не найден в переменных окружения")
