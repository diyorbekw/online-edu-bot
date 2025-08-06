import os
from datetime import datetime

import psycopg2
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.db_host = os.getenv('DB_HOST')
        self.db_port = os.getenv('DB_PORT')
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        
    @property
    def connection(self):
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        cursor = connection.cursor()
        data = None
        
        try:
            # Log the SQL query before execution
            logger(sql, parameters)
            
            cursor.execute(sql, parameters)

            if commit:
                connection.commit()
            if fetchall:
                data = cursor.fetchall()
            if fetchone:
                data = cursor.fetchone()
        except Exception as e:
            print(f"Database error: {e}")
            connection.rollback()
            raise e
        finally:
            connection.close()
        return data

    def create_table_core_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS core_user (
            telegram_id BIGINT PRIMARY KEY,
            full_name TEXT NOT NULL,
            phone_number VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = %s" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, telegram_id: int, full_name: str, phone_number: str = None):
        sql = """
        INSERT INTO core_user (telegram_id, full_name, phone_number, created_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (telegram_id) DO NOTHING;
        """
        self.execute(sql, parameters=(telegram_id, full_name, phone_number, datetime.now()), commit=True)


    def select_all_users(self):
        sql = """
        SELECT * FROM core_user;
        """
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        sql = "SELECT * FROM core_user WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters=parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM core_user;", fetchone=True)

    def delete_users(self):
        self.execute("DELETE FROM core_user WHERE TRUE;", commit=True)
    
    def all_users_id(self):
        return self.execute("SELECT telegram_id FROM core_user;", fetchall=True)
    
    def update_phone_number(self, telegram_id: int, phone_number: str):
        sql = """
        UPDATE core_user
        SET phone_number = %s
        WHERE telegram_id = %s;
        """
        self.execute(sql, parameters=(phone_number, telegram_id), commit=True)

    def get_all_faqs(self, page: int = 1, limit: int = 5):
        offset = (page - 1) * limit
        sql = """
        SELECT id, question FROM core_faq
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s;
        """
        return self.execute(sql, parameters=(limit, offset), fetchall=True)

    def get_faq_answer(self, faq_id: int):
        sql = """
        SELECT answer FROM core_faq
        WHERE id = %s;
        """
        return self.execute(sql, parameters=(faq_id,), fetchone=True)

    def count_faqs(self):
        sql = "SELECT COUNT(*) FROM core_faq;"
        return self.execute(sql, fetchone=True)

    def get_all_categories(self):
        sql = "SELECT * FROM core_category;"
        return self.execute(sql, fetchall=True)

    def get_lesson_by_category(self, category_id: int):
        sql = """
        SELECT * FROM core_lesson
        WHERE category_id = %s;
        """
        return self.execute(sql, parameters=(category_id,), fetchall=True)
    
    def get_category_by_id(self, category_id):
        sql = """
        SELECT * FROM core_category
        WHERE id = %s;
        """
        return self.execute(sql, parameters=(category_id,), fetchone=True)
    
    def get_video_by_lesson_id(self, lesson_id):
        sql = """
        SELECT * FROM core_video
        WHERE lesson_id = %s;
        """
        return self.execute(sql, parameters=(lesson_id,), fetchall=True)
    
    def get_lesson_by_id(self, lesson_id):
        sql = """
        SELECT * FROM core_lesson
        WHERE id = %s;
        """
        return self.execute(sql, parameters=(lesson_id,), fetchone=True)
    
    def get_questions_by_video_id(self, video_id):
        sql = """
        SELECT id, question, a_var, b_var, c_var, d_var, correct_answer 
        FROM core_question
        WHERE video_id = %s
        ORDER BY id;
        """
        return self.execute(sql, parameters=(video_id,), fetchall=True)
    
    def get_video_by_id(self, video_id):
        try:
            sql = """
            SELECT id, video_url, lesson_id FROM core_video
            WHERE id = %s;
            """
            return self.execute(sql, parameters=(int(video_id),), fetchall=True)
        except Exception as e:
            print(f"Error in get_video_by_id: {e}")
            return None

    def get_next_lesson(self, current_lesson_id):
        sql = """
        SELECT id FROM core_lesson
        WHERE category_id = (SELECT category_id FROM core_lesson WHERE id = %s)
        AND id > %s
        ORDER BY id ASC
        LIMIT 1;
        """
        return self.execute(sql, parameters=(current_lesson_id, current_lesson_id), fetchone=True)
    
    def add_result(self, telegram_id, correct_answers, questions_count, video_id):
        user = self.execute(
            "SELECT id FROM core_user WHERE telegram_id = %s",
            parameters=(telegram_id,),
            fetchone=True
        )
        
        if not user:
            print(f"Foydalanuvchi topilmadi (telegram_id: {telegram_id})")
            return False
        
        user_id = user[0]  
        
        video = self.execute(
            "SELECT id FROM core_video WHERE id = %s",
            parameters=(video_id,),
            fetchone=True
        )
        
        if not video:
            print(f"Video topilmadi (video_id: {video_id})")
            return False
        
        sql = """
        INSERT INTO core_result 
        (user_id, correct_answers, questions_count, video_id, created_at)
        VALUES (%s, %s, %s, %s, %s);
        """
        try:
            self.execute(
                sql, 
                parameters=(user_id, correct_answers, questions_count, video_id, datetime.now()),
                commit=True
            )
            return True
        except Exception as e:
            print(f"Natijani saqlashda xatolik: {e}")
            return False 
        
    def statistics(self, telegram_id: int) -> str:
        # 1. First verify user exists
        try:
            user_check = self.execute(
                "SELECT id FROM core_user WHERE telegram_id = %s",
                parameters=(telegram_id,),
                fetchone=True
            )
            
            if not user_check:
                return "❌ Foydalanuvchi topilmadi. Iltimos, avval ro'yxatdan o'ting."

            # 2. Get basic statistics
            stats_sql = """
            SELECT 
                COUNT(*) as total_tests,
                COALESCE(SUM(correct_answers), 0) as total_correct,
                COALESCE(SUM(questions_count), 0) as total_questions
            FROM core_result
            WHERE user_id = %s
            """
            stats = self.execute(stats_sql, parameters=(user_check[0],), fetchone=True)
            
            if not stats:
                return "📊 Hali hech qanday test natijalari mavjud emas"

            total_tests, total_correct, total_questions = stats
            total_incorrect = total_questions - total_correct
            avg_percentage = round((total_correct * 100 / total_questions), 1) if total_questions > 0 else 0

            # 3. Get recent test history
            history_sql = """
            SELECT 
                correct_answers,
                questions_count,
                created_at
            FROM core_result
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 5
            """
            history_records = self.execute(history_sql, parameters=(user_check[0],), fetchall=True)

            if history_records:
                test_history = []
                for record in history_records:
                    correct, total, date = record
                    percentage = round((correct * 100 / total), 1) if total > 0 else 0
                    test_history.append(
                        f"📅 {date.strftime('%Y-%m-%d')} | "
                        f"{correct}/{total} ({percentage}%)"
                    )
                history_text = "\n".join(test_history)
            else:
                history_text = "Hali testlar mavjud emas"

            # 4. Format the final message
            stats_text = f"""
📊 <b>Test statistikangiz:</b>

🔢 <b>Jami testlar:</b> {total_tests}

📚 <b>Jami savollar:</b> {total_questions}

✅ <b>To'g'ri javoblar:</b> {total_correct}
❌ <b>Noto'g'ri javoblar:</b> {total_incorrect}
📈 <b>O'rtacha natija:</b> {avg_percentage}%

⏳ <b>Oxirgi 5 test tarixi:</b>
{history_text}
    """
            return stats_text

        except Exception as e:
            print(f"[ERROR] statistics() failed: {str(e)}")
            return "📊 Statistika ma'lumotlarini olishda xatolik yuz berdi. Iltimos, keyinroq urunib ko'ring."

def logger(sql, parameters=None):
    print(f"""
_____________________________________________________        
Executing: 
{sql}
Parameters: {parameters}
_____________________________________________________
""")