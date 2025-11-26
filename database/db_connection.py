import os
from peewee import PostgresqlDatabase
from playhouse.db_url import connect
from loguru import logger

# Получаем DATABASE_URL из переменных окружения Railway
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Используем базу от Railway
    db = connect(DATABASE_URL)
    logger.info("✅ Using PostgreSQL from Railway DATABASE_URL")
else:
    # Локальная разработка (используем старые настройки)
    from config_data.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
    db = PostgresqlDatabase(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    logger.info("✅ Using local PostgreSQL database")

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
        # Не поднимаем исключение, чтобы бот мог работать без БД
    finally:
        if not db.is_closed():
            db.close()