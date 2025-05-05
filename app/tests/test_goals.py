from fastapi import status
from .configtest import *


def test_create_goal(client, auth_headers, goal_data):
    """Тест создания цели"""
    response = client.post(
        "/goals/",
        json=goal_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["name"] == goal_data["name"]
    assert data["target_amount"] == goal_data["target_amount"]


def test_create_goal_past_deadline(client, auth_headers, goal_data):
    """Тест создания цели с прошедшей датой"""
    invalid_data = goal_data.copy()
    invalid_data["deadline"] = (datetime.now() - timedelta(days=1)).isoformat()

    response = client.post(
        "/goals/",
        json=invalid_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Deadline cannot be in the past" in response.json()["detail"]


def test_get_goals(client, auth_headers, goal_data):
    """Тест получения списка целей"""
    # Создаем цель
    client.post("/goals/", json=goal_data, headers=auth_headers)

    # Получаем список
    response = client.get("/goals/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    goals = response.json()
    assert isinstance(goals, list)
    assert len(goals) > 0


def test_get_active_goals(client, auth_headers, goal_data):
    """Тест получения активных целей"""
    # Создаем активную цель
    client.post("/goals/", json=goal_data, headers=auth_headers)

    # Создаем завершенную цель
    completed_data = goal_data.copy()
    completed_data["current_amount"] = completed_data["target_amount"]
    client.post("/goals/", json=completed_data, headers=auth_headers)

    # Получаем только активные
    response = client.get("/goals/?active_only=true", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    goals = response.json()
    assert all(g["current_amount"] < g["target_amount"] for g in goals)


def test_get_single_goal(client, auth_headers, goal_data):
    """Тест получения конкретной цели"""
    create_resp = client.post("/goals/", json=goal_data, headers=auth_headers)
    goal_id = create_resp.json()["id"]

    response = client.get(f"/goals/{goal_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == goal_id


def test_get_nonexistent_goal(client, auth_headers):
    """Тест получения несуществующей цели"""
    response = client.get("/goals/999999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_goal(client, auth_headers, goal_data, faker):
    """Тест обновления цели"""
    # Создаем
    create_resp = client.post("/goals/", json=goal_data, headers=auth_headers)
    goal_id = create_resp.json()["id"]

    # Обновляем
    update_data = goal_data.copy()
    update_data["name"] = "Updated " + update_data["name"]
    update_data["target_amount"] = float(faker.random_number(digits=4))

    response = client.put(
        f"/goals/{goal_id}",
        json=update_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["target_amount"] == update_data["target_amount"]


def test_update_goal_past_deadline(client, auth_headers, goal_data):
    """Тест обновления с прошедшей датой"""
    create_resp = client.post("/goals/", json=goal_data, headers=auth_headers)
    goal_id = create_resp.json()["id"]

    invalid_data = goal_data.copy()
    invalid_data["deadline"] = (datetime.now() - timedelta(days=1)).isoformat()

    response = client.put(
        f"/goals/{goal_id}",
        json=invalid_data,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Deadline cannot be in the past" in response.json()["detail"]


def test_add_to_goal(client, auth_headers, goal_data):
    """Тест добавления суммы к цели"""
    create_resp = client.post("/goals/", json=goal_data, headers=auth_headers)
    goal_id = create_resp.json()["id"]

    amount_to_add = 100.0
    response = client.patch(
        f"/goals/{goal_id}/add",
        json={"amount": amount_to_add},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["current_amount"] == amount_to_add


def test_add_negative_to_goal(client, auth_headers, goal_data):
    """Тест добавления отрицательной суммы"""
    create_resp = client.post("/goals/", json=goal_data, headers=auth_headers)
    goal_id = create_resp.json()["id"]

    response = client.patch(
        f"/goals/{goal_id}/add",
        json={"amount": -100.0},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Amount must be positive" in response.json()["detail"]


def test_delete_goal(client, auth_headers, goal_data):
    """Тест удаления цели"""
    create_resp = client.post("/goals/", json=goal_data, headers=auth_headers)
    goal_id = create_resp.json()["id"]

    # Удаляем
    delete_resp = client.delete(f"/goals/{goal_id}", headers=auth_headers)
    assert delete_resp.status_code == status.HTTP_200_OK

    # Проверяем что удалилась
    get_resp = client.get(f"/goals/{goal_id}", headers=auth_headers)
    assert get_resp.status_code == status.HTTP_404_NOT_FOUND