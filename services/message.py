from typing import Dict, List
from loguru import logger


class MessageFormatter:
    """Класс для форматирования сообщений бота"""

    @staticmethod
    def filter_valid_movies(movies: List[Dict]) -> List[Dict]:
        """Фильтрует фильмы: убирает без названия и с рейтингом 0"""
        valid_movies = []
        for movie in movies:
            title = movie.get('name')
            rating_data = movie.get('rating', {})
            rating = rating_data.get('kp', 0) if rating_data else 0

            if not title or title == 'None' or rating == 0:
                continue
            valid_movies.append(movie)
        return valid_movies

    @staticmethod
    def format_movie_info(movie: Dict) -> str:
        """Форматирует информацию о фильме в читаемое сообщение для пользователя"""
        try:
            title = movie.get('name', 'Неизвестно')
            if not title or title == 'None':
                return "❌ Информация о фильме недоступна"
            year = movie.get('year', 'Неизвестно')
            if not year:
                year = 'Неизвестно'

            rating_data = movie.get('rating', {})
            rating = rating_data.get('kp', 'Н/Д') if rating_data else 'Н/Д'

            description = movie.get('description', 'Описание отсутствует')
            if not description:
                description = 'Описание отсутствует'
            elif len(description) > 300:
                description = description[:300] + '...'

            genres = movie.get('genres', [])
            genre_names = ', '.join([genre.get('name', '') for genre in genres]) if genres else 'Неизвестно'
            if not genre_names:
                genre_names = 'Неизвестно'

            age_rating = movie.get('ageRating', 'Н/Д')
            if not age_rating:
                age_rating = 'Н/Д'
            else:
                age_rating = f"{age_rating}"

            budget = movie.get('budget', {})
            budget_value = budget.get('value') if budget else None
            budget_currency = budget.get('currency', '$') if budget else '$'

            message = f"🎬 <b>{title}</b> ({year})\n"
            message += f"⭐ Рейтинг: <b>{rating}</b>/10\n"

            if budget_value:
                formatted_budget = f"{budget_value:,}".replace(',', ' ')
                message += f"💰 Бюджет: <b>{formatted_budget} {budget_currency}</b>\n"

            message += f"🎭 Жанр: <b>{genre_names}</b>\n"
            message += f"👴 Возраст: <b>{age_rating}+</b>\n"
            message += f"📖 Описание: <i>{description}</i>"

            return message
        except Exception as e:
            logger.error(f"Error formatting movie info: {e}")
            return "❌ Ошибка при форматировании информации о фильме"

    @staticmethod
    def format_search_results(movies: List[Dict], search_type: str = "результаты") -> str:
        """Форматирует и фильтрует список фильмов"""
        valid_movies = MessageFormatter.filter_valid_movies(movies)
        if not valid_movies:
            return "😔 По вашему запросу ничего не найдено"

        message = f"✅ Найдено {len(valid_movies)} {search_type}:\n\n"

        for i, movie in enumerate(valid_movies, 1):
            title = movie.get('name', 'Неизвестно')
            year = movie.get('year', '')
            rating_data = movie.get('rating', {})
            rating = rating_data.get('kp', 'Н/Д') if rating_data else 'Н/Д'

            message += f"{i}. <b>{title}</b> ({year}) - ⭐ {rating}/10\n"
        return message

    @staticmethod
    def format_history_entry(history_record: Dict) -> str:
        """Форматирует запись истории"""
        command = history_record.get('command', 'Неизвестно')
        query = history_record.get('query', '')
        created_at = history_record.get('created_at')

        if created_at:
            if isinstance(created_at, str):
                date_str = created_at
            else:
                date_str = created_at.strftime('%Y-%m-%d %H:%M')
        else:
            date_str = 'Неизвестно'

        return f"📅 {date_str} - {command}: {query}"
