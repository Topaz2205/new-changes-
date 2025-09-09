from flask import Flask
from app.routes.inventory.inventory_routes import inventory_routes
from app.routes.order_routes import order_routes  
from app.routes.access_routes import access_routes
from app.routes.main_routes import main_routes
from app.routes.auth_routes import auth_routes
from app.routes.inventory.product_routes import product_routes
from app.routes.inventory.category_routes import category_routes
from app.routes.inventory.supplier_routes import supplier_routes
from app.routes.inventory.product_color_routes import product_color_routes
from app.config import Config
from app.DB import init_db  # נדרשת לטעינה של בסיס הנתונים
import os

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)

    # יצירת מסד הנתונים אם הוא לא קיים
    if not os.path.exists(Config.DB_FILE):
        print("🔧 Database not found. Creating...")
        init_db.init_db()

    # רישום הנתיבים של כל המודולים
    app.register_blueprint(inventory_routes)
    app.register_blueprint(order_routes) 
    app.register_blueprint(access_routes)
    app.register_blueprint(main_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(product_routes)
    app.register_blueprint(category_routes)
    app.register_blueprint(supplier_routes)
    app.register_blueprint(product_color_routes)

    # הדפסת כל הנתיבים שנטענו
    print("\n--- ROUTES REGISTERED ---")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:30s} => {rule.rule}")

    return app
