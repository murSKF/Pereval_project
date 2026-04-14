import flask
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