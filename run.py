# run.py
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    # ברירת מחדל 5050; אפשר לעקוף ע"י משתנה סביבה PORT
    port = int(os.getenv("PORT", os.getenv("FLASK_RUN_PORT", "5050")))
    debug = str(os.getenv("FLASK_DEBUG", "1")).lower() in ("1","true","yes","on")
    app.run(host=host, port=port, debug=debug)
