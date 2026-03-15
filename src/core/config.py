import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_URL = (
    "postgresql+asyncpg://"
    f"{DB_USER}:{DB_PASS}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

UNIQUE_SALT = os.environ.get("UNIQUE_SALT")

JWT_SECRET = os.environ.get("JWT_SECRET")

INACTIVE_LINK_DAYS = int(os.environ.get("INACTIVE_LINK_DAYS", "30"))
