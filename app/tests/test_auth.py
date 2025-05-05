from fastapi import status
from .configtest import *

def test_register_new_user(client, valid_user_data):
    """Тест регистрации нового пользователя"""
    response = client.post(
        "/auth/register",
        json=valid_user_data
    )
    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()

def test_login_success(client, valid_user_data):
    """Тест успешной авторизации"""
    client.post("/auth/register", json=valid_user_data)

    response = client.post(
        "/auth/token",
        data={
            "username": valid_user_data["email"],
            "password": valid_user_data["password"]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

def test_login_wrong_password(client, valid_user_data):
    """Тест авторизации с неверным паролем"""
    client.post("/auth/register", json=valid_user_data)

    response = client.post(
        "/auth/token",
        data={
            "username": valid_user_data["email"],
            "password": "wrong_password"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
