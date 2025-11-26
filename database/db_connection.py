from peewee import PostgresqlDatabase
from config_data.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from loguru import logger

db = PostgresqlDatabase(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)


def init_database():
    """Инициализация базы данных PostgreSQL"""
    try:
        from database.models import create_tables

        db.connect()
        logger.info("✅ Подключение к PostgreSQL установлено")

        create_tables()
        logger.info("✅ Таблицы базы данных инициализированы")

    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
        raise
    finally:
        if not db.is_closed():
            db.close()
