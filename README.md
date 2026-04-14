# 🏔 Pereval Project API

## Описание
REST API для работы с данными о горных перевалах.

Позволяет:
- добавлять перевалы
- получать информацию о перевале
- редактировать данные (если статус = new)
- получать список перевалов пользователя

---

## Стек технологий

- Python
- Flask
- PostgreSQL
- psycopg2
- Swagger (Flasgger)
- Gunicorn
- Render (деплой)
- Supabase (база данных)

---

## API URL
https://pereval-project.onrender.com

---

## Swagger документация

Доступна по адресу: https://pereval-project.onrender.com/apidocs/


---

## Методы API

### + POST /submitData
Добавление нового перевала

**Пример запроса:**
```json
{
  "user": {
    "email": "test@mail.com",
    "fam": "Петров",
    "name": "Иван",
    "otc": "Сергеевич",
    "phone": "+79991234567"
  },
  "coords": {
    "latitude": 45.12345,
    "longitude": 7.12345,
    "height": 1200
  },
  "title": "Перевал Дятлова",
  "beautyTitle": "пер.",
  "other_titles": "Дятловский",
  "connect": "Соединяет долины",
  "winter_level": "2A",
  "summer_level": "1B",
  "autumn_level": "1B",
  "spring_level": "2A"
}
```

---

## Методы API
### GET/submitData/{id}
Получить перевал по id

### PATCH/submitData/{id}
Редактировать перевал (только если статус = new)

### GET/submitData/?user_email=<email>
Получить все перевалы пользователя

---

## Структура БД:
* users - пользователи
* coords - координаты
* pereval_added - перевалы
* pereval_images - изображения

---

## Переменные окружения
### Для подключения к БД используются:
* FSTR_DB_HOST=
* FSTR_DB_PORT=
* FSTR_DB_NAME=
* FSTR_DB_LOGIN=
* FSTR_DB_PASS=

---

## Локальный запуск
git clone https://github.com/murSKF/Pereval_project.git
cd Pereval_project

python -m venv venv
venv/Scripts/Activate

pip install -r requirements.txt

python app.py

---

## Деплой
### проект задеплоен на платформе Render

---

## Тестирование

```bash
pytest

```



