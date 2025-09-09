from flask import Blueprint, render_template, request, redirect, url_for
from app.controllers.inventory.product_color_controller import ColorController
from app.models.models_inventory.product_color import ProductColor

product_color_routes = Blueprint('product_color_routes', __name__, template_folder='../../templates')

color_controller = ColorController()

# הצגת כל הצבעים
@product_color_routes.route('/colors')
def list_colors():
    colors = color_controller.get_all_colors()
    return render_template('inventory/color/color.html', colors=colors)

# טופס הוספה
@product_color_routes.route('/colors/add', methods=['GET'])
def add_color_form():
    return render_template('inventory/color/add_color.html')

# הוספת צבע בפועל
@product_color_routes.route('/colors/add', methods=['POST'])
def add_color():
    color_name = request.form['color_name']
    hex_code = request.form.get('hex_code', '')
    color_controller.create_color(color_name, hex_code)
    return redirect(url_for('product_color_routes.list_colors'))

# טופס עריכה
@product_color_routes.route('/colors/edit/<int:color_id>', methods=['GET'])
def edit_color_form(color_id):
    color = color_controller.get_color_by_id(color_id)
    return render_template('inventory/color/edit_color.html', color=color)

# עדכון בפועל
@product_color_routes.route('/colors/edit/<int:color_id>', methods=['POST'])
def edit_color(color_id):
    updated_data = {
        "color_name": request.form['color_name'],
        "hex_code": request.form.get('hex_code', '')
    }
    color_controller.update_color(color_id, updated_data)
    return redirect(url_for('product_color_routes.list_colors'))

# מחיקה
@product_color_routes.route('/colors/delete/<int:color_id>', methods=['POST'])
def delete_color(color_id):
    color_controller.delete_color(color_id)
    return redirect(url_for('product_color_routes.list_colors'))
