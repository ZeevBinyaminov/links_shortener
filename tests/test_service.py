import pytest
from hashids import Hashids

from src.links.service import (generate_short_code, decode_short_code,
                               get_short_code, get_hashids)

hashids = Hashids(
    salt="test_salt",
    min_length=6,
)


def test_get_hashids():
    hashids_instance = get_hashids(salt="test_salt")
    assert isinstance(hashids_instance, Hashids)
    assert hashids_instance._salt == "test_salt"
    assert hashids_instance._min_length == 6


def test_generate_short_code():
    url_hash = generate_short_code(2, 1, hashids)
    assert len(url_hash) >= 6


def test_decode_short_code_normal():
    url_id = 2
    url_hash = generate_short_code(
        url_id=url_id, user_id=None, hashids_instance=hashids)
    decoded_url_id = decode_short_code(url_hash, hashids_instance=hashids)
    assert url_id == decoded_url_id


def test_decode_short_code_empty():
    decoded_url_id = decode_short_code(None, hashids_instance=hashids)
    assert decoded_url_id is None


def test_get_short_code_ex_alias():
    alias = 'testalias'
    short_code = get_short_code(
        url_id=1, alias=alias, user_id=None, hashids_instance=hashids)
    assert short_code == alias


def test_get_short_code_non_ex_alias():
    short_code = get_short_code(
        url_id=1, alias=None, user_id=None, hashids_instance=hashids)
    assert len(short_code) == 6
