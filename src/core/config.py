import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

UNIQUE_SALT = os.environ.get("UNIQUE_SALT")

JWT_SECRET = os.environ.get("JWT_SECRET")

INACTIVE_LINK_DAYS = int(os.environ.get("INACTIVE_LINK_DAYS", "30"))


# ------------TEST CONFIG------------
load_dotenv('.env-non-dev')

DB_HOST_TEST = os.environ.get("DB_HOST_TEST")
DB_PORT_TEST = os.environ.get("DB_PORT_TEST")
DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
DB_USER_TEST = os.environ.get("DB_USER_TEST")
DB_PASS_TEST = os.environ.get("DB_PASS_TEST")


REDIS_HOST_TEST = os.environ.get("REDIS_HOST_TEST")
REDIS_PORT_TEST = os.environ.get("REDIS_PORT_TEST")
REDIS_URL_TEST = f"redis://{REDIS_HOST_TEST}:{REDIS_PORT_TEST}"

UNIQUE_SALT_TEST = os.environ.get("UNIQUE_SALT_TEST")

JWT_SECRET_TEST = os.environ.get("JWT_SECRET_TEST")
