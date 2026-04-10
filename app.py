from db import FSTRDatabase
from flask import Flask, request, jsonify
import base64
from flasgger import Swagger


app = Flask(__name__)
db = FSTRDatabase()
swagger = Swagger(app)


@app.route('/submitData', methods=['POST'])
def submit_data():
    """
    Добавление нового перевала
    ---
    tags:
      - Pereval
    summary: Добавить перевал
    description: |
      Создает новую запись о перевале.

      Включает:
      - данные пользователя
      - координаты
      - уровни сложности по сезонам
      - название перевала

      После создания статус автоматически устанавливается как **new**.

    consumes:
      - application/json

    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - user
            - coords
            - title
          properties:
            user:
              type: object
              required:
                - email
                - fam
                - name
              properties:
                email:
                  type: string
                  example: test@mail.com
                fam:
                  type: string
                  example: Иванов
                name:
                  type: string
                  example: Иван
                otc:
                  type: string
                  example: Иванович
                phone:
                  type: string
                  example: "+79991234567"

            coords:
              type: object
              required:
                - latitude
                - longitude
              properties:
                latitude:
                  type: number
                  example: 45.12345
                longitude:
                  type: number
                  example: 7.12345
                height:
                  type: integer
                  example: 1200

            beautyTitle:
              type: string
              example: "пер."

            title:
              type: string
              example: "Перевал Дятлова"

            other_titles:
              type: string
              example: "Дятловский перевал"

            connect:
              type: string
              example: "Соединяет долины рек"

            winter_level:
              type: string
              example: "2A"

            summer_level:
              type: string
              example: "1B"

            autumn_level:
              type: string
              example: "1B"

            spring_level:
              type: string
              example: "2A"

    responses:
      200:
        description: Успешное добавление
        schema:
          type: object
          properties:
            status:
              type: integer
              example: 200
            message:
              type: string
              example: Отправлено успешно
            id:
              type: integer
              example: 1

      400:
        description: Ошибка в данных

      500:
        description: Внутренняя ошибка сервера
    """
    try:
        data = request.json

        # --- ВАЛИДАЦИЯ ---
        if not data or 'user' not in data:
            return jsonify({
                "status": 400,
                "message": "Некорректные данные"
            })
        
        user = data['user']
        coords = data['coords']


        # --- USER (с проверкой) ---
        user = data.get('user')

        if not user:
            return jsonify({
                "status": 400,
                "error": "Поле 'user' обязательно"
            })
        
        user_id = db.add_user(
            email=user['email'],
            phone=user.get('phone'),
            fam=user['fam'],
            name=user['name'],
            otc=user.get('otc')
        )

        # --- COORDS ---
        coords = data['coords']
        coord_id = db.add_coords(
            latitude=coords['latitude'],
            longitude=coords['longitude'],
            height=coords.get('height')
        )

        # --- PEREVAL ---
        pereval_id = db.add_pereval(
            user_id=user_id,
            coord_id=coord_id,
            title=data['title'],
            beauty_title=data.get('beautyTitle'),
            other_titles=data.get('other_titles'),
            connect=data.get('connect'),
            add_time=data.get('add_time'),
            winter_level=data.get('winter_level'),
            summer_level=data.get('summer_level'),
            autumn_level=data.get('autumn_level'),
            spring_level=data.get('spring_level')
        )

        # --- IMAGES ---
        for img in data.get('images', []):
            image_bytes = base64.b64decode(img['data'])

            db.add_image(
                pereval_id,
                image_bytes,
                img['titles'],
                img['content_type']
            )

        return jsonify({
            "status": 200,
            "user_id": user_id
        })
    
    except Exception as e:
        db.connection.rollback()
        return jsonify({
            "status": 500,
            "error": str(e)
        })
    

@app.route('/submitData/<int:pereval_id>', methods=['GET'])
def get_pereval(pereval_id):
    """
    Получить перевал по ID
    ---
    tags:
      - Pereval
    parameters:
      - name: pereval_id
        in: path
        required: true
        schema:
          type: integer
        description: ID перевала
    responses:
      200:
        description: Данные перевала
      404:
        description: Перевал не найден
      500:
        description: Ошибка сервера
    """
    try:
        data = db.get_pereval_by_id(pereval_id)

        if not data:
            return jsonify({
                "status": 404,
                "message": "Перевал не найден"
            })
        
        return jsonify(data)
    
    except Exception as e:
        return jsonify({
            "status": 500,
            "message": str(e)
        })
    

@app.route('/submitData/<int:pereval_id>', methods=['PATCH'])
def update_pereval(pereval_id):
    """
    Редактировать перевал (только если статус = new)
    ---
    tags:
      - Pereval
    parameters:
      - name: pereval_id
        in: path
        required: true
        schema:
          type: integer
        description: ID перевала

      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            coords:
              type: object
              properties:
                latitude:
                  type: number
                longitude:
                  type: number
                height:
                  type: integer
            title:
              type: string
            beautyTitle:
              type: string
            other_titles:
              type: string
            connect:
              type: string
            winter_level:
              type: string
            summer_level:
              type: string
            autumn_level:
              type: string
            spring_level:
              type: string

    responses:
      200:
        description: Результат обновления
        schema:
          type: object
          properties:
            state:
              type: integer
              example: 1
            message:
              type: string
              example: Успешно обновлено

      400:
        description: Ошибка данных

      500:
        description: Ошибка сервера
    """
    try:
        data = request.json

        result = db.update_pereval(pereval_id, data)

        return jsonify(result)
    
    except Exception as e:
        if db.connection:
            db.connection.rollback()
        return jsonify({
            "state": 0,
            "message": str(e)
        })
    

@app.route('/submitData/', methods=['GET'])
def get_by_email():
    """
    Получить все перевалы пользователя по email
    ---
    tags:
      - Pereval
    parameters:
      - name: user_email
        in: query
        required: true
        schema:
          type: string
        description: Email пользователя
    responses:
      200:
        description: Список перевалов пользователя
        schema:
          type: array
          items:
            type: object
      400:
        description: Email не указан
      500:
        description: Ошибка сервера
    """
    try:
        email = request.args.get('user_email')

        if not email:
            return jsonify({
                "status": 400,
                "message": "Не указан email"
            })
        
        data = db.get_pereval_by_email(email)

        return jsonify(data)
    
    except Exception as e:
        return jsonify({
            "status": 500,
            "message": str(e)
        })


@app.route('/')
def home():
    return {
        "message": "Pereval API is running 🚀",
        "docs": "/apidocs"
    }



if __name__ == '__main__':
    app.run(debug=True)
