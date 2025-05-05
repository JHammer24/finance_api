from fastapi import status
from .configtest import *


def test_analyze_spending(client, auth_headers, analysis_dates, setup_analytics_data):
    """Тест анализа расходов"""
    cat_id = setup_analytics_data["categories"][0]["id"]

    response = client.get(
        "/analytics/spending",
        params={
            "start_date": analysis_dates["start_date"],
            "end_date": analysis_dates["end_date"],
            "category_id": cat_id
        },
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # Проверяем структуру ответа
    assert "total_spent" in data
    assert "by_category" in data and isinstance(data["by_category"], list)
    assert "budget_comparison" in data and isinstance(data["budget_comparison"], list)
    assert "start_date" in data and "end_date" in data

    # Проверяем данные
    assert (data["total_spent"] - 150.0) < 1e-2  # Сумма расходов
    if data["by_category"]:
        category_names = [cat["category_name"] for cat in data["by_category"]]
        assert "Food" in category_names, f"Expected 'Food' in {category_names}"


def test_analyze_spending_invalid_dates(client, auth_headers, analysis_dates):
    """Тест с некорректными датами"""
    response = client.get(
        "/analytics/spending",
        params={
            "start_date": analysis_dates["end_date"],  # Намеренно перепутаны
            "end_date": analysis_dates["start_date"]
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "End date must be after start date" in response.json()["detail"]


def test_analyze_income_vs_expenses(client, auth_headers, analysis_dates, setup_analytics_data):
    """Тест сравнения доходов и расходов"""
    response = client.get(
        "/analytics/income-vs-expenses",
        params={
            "start_date": analysis_dates["start_date"],
            "end_date": analysis_dates["end_date"]
        },
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "total_income" in data and (data["total_income"] - 2000.0) < 1e-2
    assert "total_expenses" in data and (data["total_expenses"] - 150.0) < 1e-2
    assert "savings_rate" in data and 0 <= data["savings_rate"] <= 100
    assert "period" in data


def test_get_financial_health(client, auth_headers, setup_analytics_data):
    """Тест получения финансового здоровья"""
    response = client.get(
        "/analytics/financial-health",
        params={"months": 3},
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "income_vs_expenses" in data
    assert "goals_progress" in data and isinstance(data["goals_progress"], list)
    assert "analysis_period" in data

    # Проверяем структуру вложенных данных
    assert all(field in data["income_vs_expenses"] for field in
               ["total_income", "total_expenses", "savings_rate", "period"])

    if len(data["goals_progress"]) > 0:
        goal = data["goals_progress"][0]
        assert "name" in goal and goal["name"] == "Vacation"
        assert "progress" in goal and 0 <= goal["progress"] <= 100
        assert "days_left" in goal and goal["days_left"] >= 0


def test_financial_health_invalid_months(client, auth_headers):
    """Тест с невалидным количеством месяцев"""
    response = client.get(
        "/analytics/financial-health",
        params={"months": -1},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Months must be positive" in response.json()["detail"]