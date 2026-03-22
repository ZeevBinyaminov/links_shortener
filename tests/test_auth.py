import pytest

from conftest import client


def test_register_user():
    response = client.post("/auth/register", json={
        "email": "test@mail.ru",
        "password": "password"
    })
    assert response.status_code == 201


def test_login_user():
    response = client.post("/auth/jwt/login", data={
        "username": "test@mail.ru",
        "password": "password"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
