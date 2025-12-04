import os

from dotenv import load_dotenv

load_dotenv()

ADMIN_ID = 6177558353


def get_db_url():
    # Если указан DATABASE_URL, используем его
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    
    # Проверяем, есть ли настройки PostgreSQL
    postgres_user = os.getenv("POSTGRES_USER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_name = os.getenv("POSTGRES_NAME", "mainercrypto")
    
    # Если есть настройки PostgreSQL, используем их
    if postgres_user and postgres_password:
        return f'postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}/{postgres_name}'
    
    # Иначе используем SQLite для локальной разработки
    return 'sqlite+aiosqlite:///./mainercrypto.db'
