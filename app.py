from db import FSTRDatabase
from flask import Flask, request, jsonify
import base64


app = Flask(__name__)
db = FSTRDatabase()


@app.route('/submitData', methods=['POST'])
def submit_data():
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
            "status": 505,
            "message": str(e)
        })
    

@app.route('/submitData/<int:pereval_id>', methods=['PATCH'])
def update_pereval(pereval_id):
    try:
        data = request.json

        result = db.update_pereval(pereval_id, data)

        return jsonify(result)
    
    except Exception as e:
        db.connection.rollback()
        return jsonify({
            "state": 0,
            "message": str(e)
        })
    

@app.route('/submitData/', methods=['GET'])
def get_by_email():
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


if __name__ == '__main__':
    app.run(debug=True)

db.close()