from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.controllers.access.access_controller import AccessController

auth_routes = Blueprint("auth", __name__)
controller = AccessController()

@auth_routes.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("main_routes.home"))


    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        user = controller.get_user_by_credentials(username, password)
        if user:
            session["user_id"] = user.user_id
            session["username"] = user.username
            session["role"] = user.role_id
            role_name = controller.get_role_name_by_id(user.role_id)
            permissions = controller.get_permissions_by_role(role_name)
            session["permissions"] = permissions
            
            flash("התחברת בהצלחה!", "success")
            return redirect(url_for("main_routes.home"))
        else:
            flash("שם משתמש או סיסמה שגויים", "danger")

    return render_template("login.html")

@auth_routes.route("/logout")
def logout():
    session.clear()
    flash("התנתקת בהצלחה", "info")
    return redirect(url_for("auth.login"))
