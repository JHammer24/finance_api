from fastapi import status


def test_create_category(client, auth_headers, category_data):
    """Тест создания категории"""
    response = client.post(
        "/categories/",
        json=category_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == category_data["name"]
    assert data["type"] == category_data["type"]


def test_create_category_invalid_type(client, auth_headers, category_data):
    """Тест создания с невалидным типом"""
    invalid_data = category_data.copy()
    invalid_data["type"] = "invalid"

    response = client.post(
        "/categories/",
        json=invalid_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_categories(client, auth_headers, category_data):
    """Тест получения списка категорий"""
    # Создаем категорию
    client.post("/categories/", json=category_data, headers=auth_headers)

    # Получаем список
    response = client.get("/categories/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    categories = response.json()
    assert isinstance(categories, list)
    assert len(categories) == 1
    assert categories[0]["name"] == category_data["name"]


def test_get_single_category(client, auth_headers, category_data):
    """Тест получения одной категории"""
    create_resp = client.post("/categories/", json=category_data, headers=auth_headers)
    category_id = create_resp.json()["id"]

    response = client.get(f"/categories/{category_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == category_id
    assert data["name"] == category_data["name"]


def test_get_nonexistent_category(client, auth_headers):
    """Тест получения несуществующей категории"""
    response = client.get("/categories/999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_category(client, auth_headers, category_data, faker):
    """Тест обновления категории"""
    # Создаем
    create_resp = client.post("/categories/", json=category_data, headers=auth_headers)
    category_id = create_resp.json()["id"]

    # Обновляем
    update_data = {
        "name": faker.word(),
        "type": "expense" if category_data["type"] == "income" else "income"
    }

    response = client.put(
        f"/categories/{category_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["type"] == update_data["type"]


def test_delete_category(client, auth_headers, category_data):
    """Тест удаления категории"""
    create_resp = client.post("/categories/", json=category_data, headers=auth_headers)
    category_id = create_resp.json()["id"]

    # Удаляем
    delete_resp = client.delete(f"/categories/{category_id}", headers=auth_headers)
    assert delete_resp.status_code == status.HTTP_200_OK

    # Проверяем что удалилась
    get_resp = client.get(f"/categories/{category_id}", headers=auth_headers)
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND


def test_update_nonexistent_category(client, auth_headers, category_data):
    """Тест обновления несуществующей категории"""
    response = client.put(
        "/categories/999999",  # Несуществующий ID
        json=category_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Category not found"

def test_delete_nonexistent_category(client, auth_headers):
    """Тест удаления несуществующей категории"""
    response = client.delete(
        "/categories/999999",  # Несуществующий ID
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Category not found"
