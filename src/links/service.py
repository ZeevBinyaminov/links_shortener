from hashids import Hashids

from src.core.config import UNIQUE_SALT


hashids = Hashids(
    salt=UNIQUE_SALT,
    min_length=6,
)


def get_hashids(salt: str | None = None) -> Hashids:
    return Hashids(salt=salt or UNIQUE_SALT, min_length=6)


def generate_short_code(url_id: int,
                        user_id: int | None = None,
                        hashids_instance: Hashids | None = None) -> str:
    hashids_instance = hashids_instance or get_hashids()
    if user_id is None:
        return hashids_instance.encode(url_id)
    return hashids_instance.encode(user_id, url_id)


def decode_short_code(short_code: str,
                      hashids_instance: Hashids | None = None) -> int | None:
    hashids_instance = hashids_instance or get_hashids()
    decoded = hashids_instance.decode(short_code)
    if not decoded:
        return None
    return decoded[-1]


def get_short_code(
    url_id: int,
    alias: str | None = None,
    user_id: int | None = None,
    hashids_instance: Hashids | None = None
) -> str:
    if alias is not None:
        return alias
    hashids_instance = hashids_instance or get_hashids()
    return generate_short_code(url_id, user_id, hashids_instance)
