import asyncio

import pytest

from conftest import client, _cleanup_db
from src.core.config import INACTIVE_LINK_DAYS
from src.core.time import days_ago_utc_plus_3


@pytest.fixture(autouse=True, scope="function")
def clean_db():
    asyncio.run(_cleanup_db())


def register_and_login() -> dict[str, str]:
    email = "test@test.com"
    password = "password123"

    register_response = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/jwt/login",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_public_link():
    response = client.post(
        "/links/shorten",
        json={"url": "https://example.com/"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["url"].startswith("https://example.com/")
    assert data["short_code"]
    assert data["user_id"] is None


def test_get_my_links_requires_auth_for_non_empty_result():
    response = client.get("/links/my")

    assert response.status_code == 200
    assert response.json() == []


def test_create_and_list_my_links():
    headers = register_and_login()

    create_response = client.post(
        "/links/shorten",
        json={"url": "https://example.com/"},
        headers=headers,
    )
    assert create_response.status_code == 201

    list_response = client.get("/links/my", headers=headers)

    assert list_response.status_code == 200
    data = list_response.json()
    assert len(data) == 1
    link = data[0]
    assert create_response.json()["id"] == link["id"]


def test_search_link_by_original_url():
    original_url = f"https://example.com/"
    create_response = client.post(
        "/links/shorten",
        json={"url": original_url},
    )
    assert create_response.status_code == 201

    search_response = client.get(
        "/links/search", params={"original_url": original_url})

    assert search_response.status_code == 200
    assert search_response.json()["url"] == original_url


def test_redirect_by_short_code():
    create_response = client.post(
        "/links/shorten",
        json={"url": "https://example.com/"},
    )
    assert create_response.status_code == 201
    short_code = create_response.json()["short_code"]
    original_url = create_response.json()["url"]

    redirect_response = client.get(
        f"/links/{short_code}",
        follow_redirects=False,
    )

    assert redirect_response.status_code == 302
    assert redirect_response.headers["location"] == original_url


def test_get_link_stats():
    create_response = client.post(
        "/links/shorten",
        json={"url": "https://example.com/"},
    )
    assert create_response.status_code == 201
    short_code = create_response.json()["short_code"]

    client.get(f"/links/{short_code}", follow_redirects=False)
    stats_response = client.get(f"/links/{short_code}/stats")

    assert stats_response.status_code == 200
    data = stats_response.json()
    assert data["redirects_count"] == 1
    assert data["last_used_at"] is not None


def test_update_link_requires_owner_token():
    create_response = client.post(
        "/links/shorten",
        json={"url": "https://example.com/"},
    )
    assert create_response.status_code == 201
    short_code = create_response.json()["short_code"]

    update_response = client.put(
        f"/links/{short_code}",
        json={"url": "https://updated.example.com/"},
    )

    assert update_response.status_code == 401


def test_update_and_delete_owned_link():
    headers = register_and_login()
    url = "https://example.com/"
    create_response = client.post(
        "/links/shorten",
        json={"url": url},
        headers=headers,
    )
    assert create_response.status_code == 201
    short_code = create_response.json()["short_code"]
    new_short_code = f"new{short_code}"

    update_response = client.put(
        f"/links/{short_code}",
        json={"url": url, "alias": new_short_code},
        headers=headers,
    )

    assert update_response.status_code == 200
    assert update_response.json()["short_code"] == new_short_code

    delete_response = client.delete(
        f"/links/{new_short_code}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    get_response = client.get(
        f"/links/{new_short_code}", follow_redirects=False)
    assert get_response.status_code == 404


def test_delete_expired_owned_link():
    headers = register_and_login()
    url = "https://example.com/"
    create_response = client.post(
        "/links/shorten",
        json={"url": url,
              "expires_at": "2000-01-01T00:00:00Z"},
        headers=headers,
    )
    assert create_response.status_code == 201
    short_code = create_response.json()["short_code"]

    delete_response = client.delete(
        f"/links/{short_code}",
        headers=headers,
    )

    assert delete_response.status_code == 404


def test_create_existing_alias():
    url = "https://example.com/"
    alias = "customalias"
    create_response1 = client.post(
        "/links/shorten",
        json={"url": url, "alias": alias},
    )
    assert create_response1.status_code == 201

    create_response2 = client.post(
        "/links/shorten",
        json={"url": url, "alias": alias},
    )
    assert create_response2.status_code == 409


def test_update_link_to_busy_alias():
    headers = register_and_login()
    url1 = "https://example.com/1"
    url2 = "https://example.com/2"
    alias1 = "alias1"
    alias2 = "alias2"

    create_response1 = client.post(
        "/links/shorten",
        json={"url": url1, "alias": alias1},
        headers=headers,
    )
    assert create_response1.status_code == 201

    create_response2 = client.post(
        "/links/shorten",
        json={"url": url2, "alias": alias2},
        headers=headers,
    )
    assert create_response2.status_code == 201

    short_code1 = create_response1.json()["short_code"]

    update_response = client.put(
        f"/links/{short_code1}",
        json={"url": url2, "alias": alias1},
        headers=headers
    )
    assert update_response.status_code == 409
