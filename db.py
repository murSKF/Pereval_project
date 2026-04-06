from dotenv import load_dotenv
import psycopg2
import os

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
        
    
