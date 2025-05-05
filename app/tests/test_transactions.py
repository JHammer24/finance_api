from fastapi import status
from datetime import datetime, timedelta
from .configtest import *


def test_create_transaction(client, auth_headers, transaction_data):
    """Тест создания транзакции"""
    response = client.post(
        "/transactions/",
        json=transaction_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["amount"] == transaction_data["amount"]
    assert data["category_id"] == transaction_data["category_id"]


def test_create_transaction_invalid_category(client, auth_headers, transaction_data):
    """Тест создания транзакции с несуществующей категорией"""
    invalid_data = transaction_data.copy()
    invalid_data["category_id"] = 999999

    response = client.post(
        "/transactions/",
        json=invalid_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Category not found"


def test_get_transactions(client, auth_headers, transaction_data):
    """Тест получения списка транзакций"""
    # Создаем транзакцию
    create_resp = client.post("/transactions/", json=transaction_data, headers=auth_headers)

    # Получаем список
    response = client.get("/transactions/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    transactions = response.json()
    assert isinstance(transactions, list)
    assert len(transactions) == 1
    assert transactions[0]["amount"] == transaction_data["amount"]


def test_get_transactions_by_category(client, auth_headers, transaction_data, category):
    """Тест фильтрации транзакций по категории"""
    # Создаем транзакцию
    client.post("/transactions/", json=transaction_data, headers=auth_headers)

    # Фильтруем по категории
    response = client.get(
        f"/transactions/?category_id={category['id']}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


def test_get_transactions_by_period(client, auth_headers, transaction_data):
    """Тест фильтрации транзакций по периоду"""
    # Создаем транзакцию
    client.post("/transactions/", json=transaction_data, headers=auth_headers)

    # Фильтруем по периоду
    today = datetime.now().date()
    start_date = (today - timedelta(days=366)).isoformat()
    end_date = today.isoformat()

    response = client.get(
        f"/transactions/?start_date={start_date}&end_date={end_date}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


def test_get_transactions_invalid_period(client, auth_headers):
    """Тест фильтрации с некорректным периодом"""
    today = datetime.now().date()
    start_date = today.isoformat()
    end_date = (today - timedelta(days=1)).isoformat()

    response = client.get(
        f"/transactions/?start_date={start_date}&end_date={end_date}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "End date must be after start date" in response.json()["detail"]


def test_get_single_transaction(client, auth_headers, transaction_data):
    """Тест получения конкретной транзакции"""
    create_resp = client.post("/transactions/", json=transaction_data, headers=auth_headers)
    transaction_id = create_resp.json()["id"]

    response = client.get(
        f"/transactions/{transaction_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == transaction_id


def test_get_nonexistent_transaction(client, auth_headers):
    """Тест получения несуществующей транзакции"""
    response = client.get("/transactions/999999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_transaction(client, auth_headers, transaction_data, faker):
    """Тест обновления транзакции"""
    # Создаем
    create_resp = client.post("/transactions/", json=transaction_data, headers=auth_headers)
    transaction_id = create_resp.json()["id"]

    # Обновляем
    update_data = transaction_data.copy()
    update_data["amount"] = float(faker.random_number(digits=3))
    update_data["description"] = "Updated description"

    response = client.put(
        f"/transactions/{transaction_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["amount"] == update_data["amount"]
    assert data["description"] == update_data["description"]


def test_update_nonexistent_transaction(client, auth_headers, transaction_data):
    """Тест обновления несуществующей транзакции"""
    response = client.put(
        "/transactions/999999",
        json=transaction_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_transaction(client, auth_headers, transaction_data):
    """Тест удаления транзакции"""
    create_resp = client.post("/transactions/", json=transaction_data, headers=auth_headers)
    transaction_id = create_resp.json()["id"]

    # Удаляем
    delete_resp = client.delete(f"/transactions/{transaction_id}", headers=auth_headers)
    assert delete_resp.status_code == status.HTTP_200_OK

    # Проверяем что удалилась
    get_resp = client.get(f"/transactions/{transaction_id}", headers=auth_headers)
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_transaction(client, auth_headers):
    """Тест удаления несуществующей транзакции"""
    response = client.delete("/transactions/999999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND