# access_routes.py (updated)
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers.access.access_controller import AccessController
from app.utils.decorators import login_required, permission_required

access_routes = Blueprint("access", __name__, url_prefix="/access")
controller = AccessController()

# --- Users ---
@access_routes.route("/users")
@login_required
@permission_required("view_users")
def users_list():
    users = controller.get_all_users()
    return render_template("access/users.html", users=users, controller=controller)

@access_routes.route("/users/add", methods=["GET", "POST"])
@login_required
@permission_required("manage_users")
def add_user():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role_id = int(request.form["role_id"])
        controller.add_user(username, email, password, role_id)
        flash("המשתמש נוסף בהצלחה!", "success")
        return redirect(url_for("access.users_list"))
    roles = controller.get_all_roles()
    return render_template("access/add_user.html", roles=roles)

@access_routes.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
@permission_required("manage_users")
def edit_user(user_id):
    user_row = controller.get_user_by_id(user_id)
    if not user_row:
        flash("משתמש לא נמצא", "error")
        return redirect(url_for("access.users_list"))

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role_id = int(request.form["role_id"])
        controller.update_user(user_id, username, email, password, role_id)
        flash("המשתמש עודכן בהצלחה!", "success")
        return redirect(url_for("access.users_list"))

    roles = controller.get_all_roles()
    return render_template("access/edit_user.html", user=user_row, roles=roles)

@access_routes.route("/users/delete/<int:user_id>", methods=["POST"])
@login_required
@permission_required("manage_users")
def delete_user(user_id):
    controller.delete_user(user_id)
    flash("המשתמש נמחק בהצלחה!", "success")
    return redirect(url_for("access.users_list"))

# --- Roles ---
@access_routes.route("/roles")
@login_required
@permission_required("view_users")
def roles_list():
    roles = controller.get_all_roles()
    return render_template("access/roles.html", roles=roles)

@access_routes.route("/roles/add", methods=["GET", "POST"])
@login_required
@permission_required("manage_users")
def add_role():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        controller.add_role(name, description)
        flash("התפקיד נוסף בהצלחה!", "success")
        return redirect(url_for("access.roles_list"))
    return render_template("access/add_role.html")

# --- Permissions ---
@access_routes.route("/permissions")
@login_required
@permission_required("view_users")
def permissions_list():
    permissions = controller.get_all_permissions()
    return render_template("access/permissions.html", permissions=permissions)

@access_routes.route("/permissions/add", methods=["GET", "POST"])
@login_required
@permission_required("manage_users")
def add_permission():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        controller.add_permission(name, description)
        flash("ההרשאה נוספה בהצלחה!", "success")
        return redirect(url_for("access.permissions_list"))
    return render_template("access/add_permission.html")
