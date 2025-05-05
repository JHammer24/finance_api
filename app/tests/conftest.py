import os
from datetime import datetime, timedelta
import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from ..main import app
from ..database import Base, get_db


# Загрузка тестовых переменных окружения
load_dotenv(os.path.join(os.path.dirname(__file__), '.env.test'))

# Настройка тестовой БД
TEST_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def setup_database():
    """Создание и удаление таблиц перед/после всех тестов"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db(setup_database):
    """Фикстура для тестовой сессии БД с откатом транзакций"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    """Фикстура тестового клиента с подменой БД"""

    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def faker():
    return Faker()


@pytest.fixture()
def valid_user_data(faker):
    return {
        "email": faker.email(),
        "password": faker.password(length=12),
    }


@pytest.fixture()
def auth_headers(client, valid_user_data):
    """Фикстура для авторизованных запросов"""
    # Регистрация
    client.post("/auth/register", json=valid_user_data)

    # Логин
    login_response = client.post(
        "/auth/token",
        data={
            "username": valid_user_data["email"],
            "password": valid_user_data["password"]
        }
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def category_data(faker):
    return {
        "name": faker.word(),
        "type": faker.random_element(elements=("income", "expense"))
    }


@pytest.fixture()
def category(client, auth_headers, category_data):
    """Фикстура для создания тестовой категории"""
    response = client.post(
        "/categories/",
        json=category_data,
        headers=auth_headers
    )
    return response.json()


@pytest.fixture()
def transaction_data(faker, category):
    """Генерирует тестовые данные для транзакции"""
    return {
        "amount": float(faker.random_number(digits=2)),
        "description": faker.sentence(),
        "date": faker.date_this_year().isoformat(),
        "category_id": category["id"]
    }


@pytest.fixture()
def budget_data(faker, category):
    """Генерирует тестовые данные для бюджета"""
    return {
        "amount": float(faker.random_number(digits=4)),
        "period": "month",
        "category_id": category["id"]
    }


@pytest.fixture()
def goal_data(faker):
    """Генерирует тестовые данные для цели"""
    return {
        "name": faker.sentence(),
        "target_amount": float(faker.random_number(digits=4)),
        "current_amount": 0.0,
        "deadline": (datetime.now() + timedelta(days=30)).isoformat()
    }


@pytest.fixture
def analysis_dates():
    today = datetime.now().date()
    return {
        "start_date": (today - timedelta(days=30)).isoformat(),
        "end_date": today.isoformat()
    }


@pytest.fixture
def setup_analytics_data(client, auth_headers):
    """Фикстура для создания тестовых данных"""
    # Создаем категории
    categories = [
        {"name": "Food", "type": "expense"},
        {"name": "Salary", "type": "income"}
    ]
    created_cats = []
    for cat in categories:
        response = client.post("/categories/", json=cat, headers=auth_headers)
        created_cats.append(response.json())

    # Создаем транзакции
    transactions = [
        {"amount": 150.0, "category_id": created_cats[0]["id"], "date": datetime.now().isoformat()},
        {"amount": 2000.0, "category_id": created_cats[1]["id"], "date": datetime.now().isoformat()}
    ]
    for tr in transactions:
        client.post("/transactions/", json=tr, headers=auth_headers)

    # Создаем бюджет
    budget = {
        "amount": 500.0,
        "period": "month",
        "category_id": created_cats[0]["id"]
    }
    client.post("/budgets/", json=budget, headers=auth_headers)

    # Создаем цель
    goal = {
        "name": "Vacation",
        "target_amount": 5000.0,
        "current_amount": 1000.0,
        "deadline": (datetime.now() + timedelta(days=30)).isoformat()
    }
    client.post("/goals/", json=goal, headers=auth_headers)

    return {
        "categories": created_cats,
        "transactions": transactions,
        "budget": budget,
        "goal": goal
    }
