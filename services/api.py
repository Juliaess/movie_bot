import requests
from typing import Dict, Optional
from config_data.config import BASE_URL, API_KEY
from loguru import logger


class KinopoiskAPI:
    """Клиент для работы с Kinopoisk API"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'X-API-KEY': API_KEY})

    def search_movie(self, query: str, limit: int = 10, page: int = 1) -> Optional[Dict]:
        """Ищет фильмы по названию"""
        endpoint = f"{BASE_URL}/movie/search"
        params = {
            'query': query,
            'limit': limit,
            'page': page
        }

        try:
            logger.info(f"Searching movies: {query}")
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error in search_movie: {e}")
            return None

    def get_movies_by_rating(self, min_rating: float = 7.0, max_rating: float = 10.0, genre: str = None, limit: int = 10, page: int = 1) -> Optional[Dict]:
        """Ищет фильмы по рейтингу"""
        endpoint = f"{BASE_URL}/movie"
        params = {
            'selectFields': ['id', 'name', 'rating', 'year', 'description', 'genres', 'ageRating', 'poster'],
            'rating.kp': f'{min_rating}-{max_rating}',
            'sortField': 'rating.kp',
            'sortType': '-1',
            'limit': limit,
            'page': page
        }
        if genre:
            params['genres.name'] = genre

        try:
            logger.info(f"Fetching movies by rating: {min_rating}-{max_rating}")
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error in get_movies_by_rating: {e}")
            return None

    def get_low_budget_movies(self, genre: str = None, limit: int = 10, page: int = 1) -> Optional[Dict]:
        """Ищет фильмы с низким бюджетом"""
        endpoint = f"{BASE_URL}/movie"
        params = {
            'selectFields': ['id', 'name', 'rating', 'year', 'description', 'genres', 'ageRating', 'poster', 'budget'],
            'budget.value': '1000-1000000',
            'notNullFields': ['budget.value'],
            'sortField': 'budget.value',
            'sortType': '1',
            'limit': limit,
            'page': page
        }
        if genre:
            params['genres.name'] = genre

        try:
            logger.info("Fetching low budget movies")
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error in get_low_budget_movies: {e}")
            return None

    def get_high_budget_movies(self, genre: str = None, limit: int = 10, page: int = 1) -> Optional[Dict]:
        """Ищет фильмы с высоким бюджетом"""
        endpoint = f"{BASE_URL}/movie"
        params = {
            'selectFields': ['id', 'name', 'rating', 'year', 'description', 'genres', 'ageRating', 'poster', 'budget'],
            'budget.value': '100000000-500000000',
            'notNullFields': ['budget.value'],
            'sortField': 'budget.value',
            'sortType': '-1',
            'limit': limit,
            'page': page
        }
        if genre:
            params['genres.name'] = genre

        try:
            logger.info("Fetching high budget movies")
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error in get_high_budget_movies: {e}")
            return None

    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Получает детальную информацию о фильме"""
        endpoint = f"{BASE_URL}/movie/{movie_id}"

        try:
            logger.info(f"Fetching movie details: {movie_id}")
            response = self.session.get(endpoint)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error in get_movie_details: {e}")
            return None


kinopoisk_api = KinopoiskAPI()
