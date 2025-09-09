from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.controllers.inventory.inventory_controller import InventoryController
from app.utils.decorators import login_required, permission_required  # ייבוא הדקורטור



inventory_routes = Blueprint("inventory", __name__, url_prefix="/inventory")

controller = InventoryController()

@inventory_routes.route("/")
@login_required
@permission_required("view_inventory")
def inventory_list():
    inventory_data = controller.get_all_stock()
    return render_template("inventory/list.html", inventory=inventory_data)

@inventory_routes.route("/update/<int:product_id>", methods=["GET", "POST"])
@login_required
@permission_required("manage_inventory")
def update_stock(product_id):
    inventory_item = controller.get_stock_level(product_id)
    if not inventory_item:
        flash("פריט לא נמצא במלאי", "error")
        return redirect(url_for("inventory.inventory_list"))

    if request.method == "POST":
        try:
            qty = int(request.form.get("amount"))
            controller.add_stock(product_id, qty)
            flash("המלאי עודכן בהצלחה!", "success")
            return redirect(url_for("inventory.inventory_list"))
        except ValueError:
            flash("יש להזין מספר תקין", "error")

    return render_template("inventory/update.html", inventory_id=product_id, inventory_item=inventory_item)
