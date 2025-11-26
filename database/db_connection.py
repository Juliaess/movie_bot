import os
from playhouse.db_url import connect
from loguru import logger

DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    try:
        db = connect(DATABASE_URL)
        logger.info("✅ Using PostgreSQL from Railway DATABASE_URL")
    except Exception as e:
        logger.error(f"❌ Failed to connect via DATABASE_URL: {e}")
        db = None
else:
    logger.warning("⚠️ DATABASE_URL not found, database disabled")
    db = None


def init_database():
    """Инициализация базы данных"""
    if not db:
        logger.warning("⚠️ Database not available, skipping initialization")
        return

    try:
        from database.models import create_tables
        db.connect()
        logger.info("✅ Подключение к PostgreSQL установлено")
        create_tables()
        logger.info("✅ Таблицы базы данных инициализированы")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
    finally:
        if db and not db.is_closed():
            db.close()
