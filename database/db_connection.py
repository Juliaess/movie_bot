from peewee import SqliteDatabase
from loguru import logger

db = SqliteDatabase('movie_bot.db', pragmas={'journal_mode': 'wal'})
logger.info("✅ Using SQLite database")


def init_database():
    """Инициализация базы данных SQLite"""
    try:
        from database.models import create_tables

        db.connect()
        logger.info("✅ Подключение к SQLite установлено")

        create_tables()
        logger.info("✅ Таблицы базы данных инициализированы")

    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
    finally:
        pass
