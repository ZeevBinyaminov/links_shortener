from hashids import Hashids

from src.core.config import UNIQUE_SALT


hashids = Hashids(
    salt=UNIQUE_SALT,
    min_length=6,
)


def generate_short_code(url_id: int, user_id: int | None = None) -> str:
    if user_id is None:
        user_id = -1
    return hashids.encode(user_id, url_id)


def decode_short_code(short_code: str) -> int | None:
    decoded = hashids.decode(short_code)
    if not decoded:
        return None
    return decoded[-1]


def get_short_code(
    url_id: int,
    alias: str | None = None,
    user_id: int | None = None,
) -> str:
    if alias:
        return alias
    return generate_short_code(url_id, user_id)
