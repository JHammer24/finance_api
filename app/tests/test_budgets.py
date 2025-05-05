from fastapi import status
from .configtest import *


def test_create_budget(client, auth_headers, budget_data):
    """Тест создания бюджета"""
    response = client.post(
        "/budgets/",
        json=budget_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["amount"] == budget_data["amount"]
    assert data["category_id"] == budget_data["category_id"]


def test_create_budget_invalid_category(client, auth_headers, budget_data):
    """Тест создания бюджета с несуществующей категорией"""
    invalid_data = budget_data.copy()
    invalid_data["category_id"] = 999999

    response = client.post(
        "/budgets/",
        json=invalid_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Category not found"


def test_create_duplicate_budget(client, auth_headers, budget_data):
    """Тест создания дубликата бюджета для категории"""
    # Первое создание
    client.post("/budgets/", json=budget_data, headers=auth_headers)

    # Попытка создать второй бюджет для той же категории
    response = client.post(
        "/budgets/",
        json=budget_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Budget for this category already exists" in response.json()["detail"]


def test_get_budgets(client, auth_headers, budget_data):
    """Тест получения списка бюджетов"""
    # Создаем бюджет
    create_resp = client.post("/budgets/", json=budget_data, headers=auth_headers)

    # Получаем список
    response = client.get("/budgets/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    budgets = response.json()
    assert isinstance(budgets, list)
    assert len(budgets) == 1
    assert budgets[0]["amount"] == budget_data["amount"]


def test_get_single_budget(client, auth_headers, budget_data):
    """Тест получения конкретного бюджета"""
    create_resp = client.post("/budgets/", json=budget_data, headers=auth_headers)
    budget_id = create_resp.json()["id"]

    response = client.get(
        f"/budgets/{budget_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == budget_id


def test_get_nonexistent_budget(client, auth_headers):
    """Тест получения несуществующего бюджета"""
    response = client.get("/budgets/999999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_budget(client, auth_headers, budget_data, faker):
    """Тест обновления бюджета"""
    # Создаем
    create_resp = client.post("/budgets/", json=budget_data, headers=auth_headers)
    budget_id = create_resp.json()["id"]

    # Обновляем
    update_data = budget_data.copy()
    update_data["amount"] = float(faker.random_number(digits=3))

    response = client.put(
        f"/budgets/{budget_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["amount"] == update_data["amount"]


def test_update_budget_invalid_category(client, auth_headers, budget_data):
    """Тест обновления бюджета с несуществующей категорией"""
    # Создаем бюджет
    create_resp = client.post("/budgets/", json=budget_data, headers=auth_headers)
    budget_id = create_resp.json()["id"]

    # Пытаемся обновить с неверной категорией
    invalid_data = budget_data.copy()
    invalid_data["category_id"] = 999999

    response = client.put(
        f"/budgets/{budget_id}",
        json=invalid_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Category not found" in response.json()["detail"]


def test_update_nonexistent_budget(client, auth_headers, budget_data):
    """Тест обновления несуществующего бюджета"""
    response = client.put(
        "/budgets/999999",
        json=budget_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_budget(client, auth_headers, budget_data):
    """Тест удаления бюджета"""
    create_resp = client.post("/budgets/", json=budget_data, headers=auth_headers)
    budget_id = create_resp.json()["id"]

    # Удаляем
    delete_resp = client.delete(f"/budgets/{budget_id}", headers=auth_headers)
    assert delete_resp.status_code == status.HTTP_200_OK

    # Проверяем что удалился
    get_resp = client.get(f"/budgets/{budget_id}", headers=auth_headers)
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_budget(client, auth_headers):
    """Тест удаления несуществующего бюджета"""
    response = client.delete("/budgets/999999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND