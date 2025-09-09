import os

class Config:
    SECRET_KEY = 'your-secret-key-change-this'

    # בסיס הפרויקט (השורש)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # נתיב למסד הנתונים
    DB_FILE = os.path.join(BASE_DIR, 'app', 'DB', 'database.db')
