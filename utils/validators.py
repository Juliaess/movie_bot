import re
from typing import Optional, Tuple


def validate_rating_input(text: str) -> Tuple[bool, Optional[float], Optional[float]]:
    """Валидация ввода для рейтинга"""
    try:
        if '-' in text:
            parts = text.split('-')
            if len(parts) == 2:
                min_rating = float(parts[0].strip())
                max_rating = float(parts[1].strip())

                if 0 <= min_rating <= 10 and 0 <= max_rating <= 10 and min_rating <= max_rating:
                    return True, min_rating, max_rating
    except ValueError:
        pass

    return False, None, None


def validate_search_query(text: str) -> bool:
    """Валидация поисковых запросов"""
    if not text or len(text.strip()) < 2:
        return False

    if len(text.strip()) > 100:
        return False

    if re.match(r'^[^\wа-яА-Я]+$', text):
        return False

    return True


def validate_limit_input(text: str, max_limit: int = 20) -> Tuple[bool, Optional[int]]:
    """Валидация ввода для лимита результатов"""
    try:
        limit = int(text.strip())
        if 1 <= limit <= max_limit:
            return True, limit
    except ValueError:
        pass

    return False, None
