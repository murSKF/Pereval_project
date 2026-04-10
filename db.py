from dotenv import load_dotenv
import psycopg2
import os
from psycopg2.extras import RealDictCursor


load_dotenv()

class FSTRDatabase:
    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                host = os.getenv('FSTR_DB_HOST'),
                port = os.getenv('FSTR_DB_PORT'),
                database = os.getenv('FSTR_DB_NAME'),
                user = os.getenv('FSTR_DB_LOGIN'),
                password = os.getenv('FSTR_DB_PASS'),
            )
            print("Подключение к БД успешно")
        except Exception as e:
            print("Ошибка подключения:", e)

    def close(self):
        if self.connection:
            self.connection.close()


    def add_user(self, email, phone, fam, name, otc):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (email, phone, fam, name, otc)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET email = EXCLUDED.email
                RETURNING id
            """, (email, phone, fam, name, otc))
            user_id = cursor.fetchone()[0]
            self.connection.commit()
            return user_id
    

    def add_coords(self, latitude, longitude, height=None):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO coords(latitude, longitude, height)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (latitude, longitude, height))
            
            coord_id = cursor.fetchone()[0]
            self.connection.commit()
            return coord_id


    def add_pereval(self, user_id, coord_id, title, 
                    beauty_title=None, other_titles=None, connect=None,
                    add_time=None, winter_level=None, summer_level=None,
                    autumn_level=None, spring_level=None):
        
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO pereval_added
                (user_id, coord_id, title, "beautyTitle", other_titles, 
                connect, add_time, winter_level, summer_level,
                autumn_level, spring_level, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'new')
                RETURNING id
            """, (
            user_id, coord_id, title, beauty_title, other_titles, connect, 
            add_time, winter_level, summer_level, autumn_level, spring_level))
            
            pereval_id = cursor.fetchone()[0]
            self.connection.commit()
            return pereval_id
        

    def add_image(self, pereval_id, img, filename, content_type):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO pereval_images
                (pereval_id, img, filename, content_type)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (pereval_id, img, filename, content_type))
            
            image_id = cursor.fetchone()[0]
            self.connection.commit()
            return image_id
        
    
    def get_pereval_by_id(self, pereval_id: int):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT p.*, u.email, u.phone, u.fam, u.name, u.otc, c.latitude, c.longitude, c.height
                FROM pereval_added p
                JOIN users u ON p.user_id = u.id
                LEFT JOIN coords c ON p.coord_id = c.id
                WHERE p.id = %s
            """, (pereval_id,))

            pereval = cursor.fetchone()

            if not pereval:
                return None
            
            # изображения
            cursor.execute("""
                SELECT filename, content_type
                FROM pereval_images
                WHERE pereval_id = %s
            """, (pereval_id,))

            pereval['images'] = cursor.fetchone()

            return pereval
        

    def update_pereval(self, pereval_id: int, data: dict):
        with self.connection.cursor() as cursor:

            # проверка статуса
            cursor.execute("""
                SELECT status FROM pereval_added WHERE id = %s
            """, (pereval_id,))
            result = cursor.fetchone()

            if not result:
                return {"state": 0, "message": "Запись не найдена"}
            
            if result[0] != 'new':
                return {"state": 0, "message": "Можно редактировать только записи со статусом 'new'"}
            
            # --- обновляем pereval ---
            cursor.execute("""
                UPDATE pereval_added
                SET "beautyTitle"=%s, title=%s, other_titles=%s,
                    connect=%s, add_time=%s,
                    winter_level=%s, summer_level=%s,
                    autumn_level=%s, spring_level=%s
                WHERE id=%s
            """, (
                data.get('beautyTitle'),
                data.get('title'),
                data.get('other_titles'),
                data.get('connect'),
                data.get('add_time'),
                data.get('winter'),
                data.get('summer'),
                data.get('autumn'),
                data.get('spring'),
                pereval_id
            ))

            # --- обновляем coords ---
            coords = data.get('coords', {})
            cursor.execute("""
                UPDATE coords
                SET latitude=%s, longitude=%s, height=%s
                WHERE id=(SELECT coord_id FROM pereval_added WHERE id=%s)
            """, (
                coords.get('latitude'),
                coords.get('longitude'),
                coords.get('height'),
                pereval_id
            ))

            self.connection.commit()

            return {"state": 1, "message": "Запись обновлена"}


    def get_pereval_by_email(self, email: str):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT p.id, p.title, p.status, p.date_added
                FROM pereval_added p
                JOIN users u ON p.user_id = u.id
                WHERE u.email = %s
            """, (email,))

            return cursor.fetchall()