import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db import FSTRDatabase


@pytest.fixture
def db():
    db = FSTRDatabase()
    yield db
    db.connection.rollback()
    db.close()


def test_add_user(db):
    user_id = db.add_user(
        email="test@test.com",
        fam="Петров",
        name="Иван"
    )

    assert user_id is not None


def test_add_coords(db):
    coord_id = db.add_coords(45.0, 7.0, 1000)
    assert coord_id is not None


def test_add_pereval(db):
    user_id = db.add_user("test@test.com", "123", "Петров", "Иван")
    coord_id = db.add_coords(45.0, 7.0, 1000)

    pereval_id = db.add_pereval(
        user_id=user_id,
        coord_id=coord_id,
        title="Тест перевал"
    )

    assert pereval_id is not None


def test_get_pereval(db):
    user_id = db.add_user("test@test.com", "123", "Петров", "Иван")
    coord_id = db.add_coords(45.0, 7.0, 1000)

    pereval_id = db.add_pereval(user_id, coord_id, title="Test")

    data = db.get_pereval_by_id(pereval_id)

    assert data is not None
    assert data["title"] == "Test"

