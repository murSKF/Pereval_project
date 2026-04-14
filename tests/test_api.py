import flask
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import pytest
from app import app, get_by_email


@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()


def test_submit_and_get(client):
    # 1. Отправляем POST
    response = client.post('/submitData', json={
        "user": {
            "email": "apitest@test.com",
            "fam": "Петров",
            "name": "Иван"
        },
        "coords": {
            "latitude": 45.0,
            "longitude": 7.0
        },
        "title": "API тест"
    })

    assert response.status_code == 200

    data = response.get_json()
    pereval_id = data.get("id")

    # 2. Получаем через GET
    response = client.get(f'/submitData/{pereval_id}')
    assert response.status_code == 200

    data = response.get_json()
    assert data["title"] == "API тест"


def test_update_pereval(client):
    # создаем
    response = client.post('/submitData', json={
        "user": {
            "email": "patch@test.com",
            "fam": "Петров",
            "name": "Иван"
        },
        "coords": {
            "latitude": 45.0,
            "longitude": 7.0
        },
        "title": "Старое имя"
    })

    pereval_id = response.get_json()["id"]

    # обновляем
    response = client.patch(f'/submitData/{pereval_id}', json={
        "title": "Новое имя"
    })

    assert response.status_code == 200


def test_get_by_email(client):
    email = "email@test.com"

    client.post('/submitData', json={
        "user": {
            "email": email,
            "fam": "Петров",
            "name": "Иван"
        },
        "coords": {
            "latitude": 45.0,
            "longitude": 7.0
        },
        "title": "Email тест"
    })

    response = client.get(f'/submitData/?user_email={email}')
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)


