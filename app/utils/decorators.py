from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # אם המשתמש לא מחובר – הפניה לדף התחברות
        if "user_id" not in session:
            flash("אנא התחבר תחילה.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def permission_required(permission_name):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # ראשית נוודא שהמשתמש מחובר – אחרת לא בודקים הרשאות בכלל
            if "user_id" not in session:
                return redirect(url_for("auth.login"))  # ללא flash חוזר – כדי למנוע כפילויות
            permissions = session.get("permissions", [])
            if permission_name not in permissions:
                flash("אין לך הרשאה לגשת לעמוד זה.", "danger")
                return redirect(url_for("main_routes.home"))
            return f(*args, **kwargs)
        return wrapper
    return decorator
