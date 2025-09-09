from flask import Blueprint, render_template, request, redirect, url_for
from app.controllers.inventory.category_controller import CategoryController
from app.models.models_inventory.category import Category

category_routes = Blueprint('category_routes', __name__, template_folder='../../templates')

category_controller = CategoryController()

# הצגת כל הקטגוריות
@category_routes.route('/categories')
def list_categories():
    categories = category_controller.get_all_categories()
    return render_template('inventory/categories/category.html', categories=categories)

# טופס להוספת קטגוריה חדשה
@category_routes.route('/categories/add', methods=['GET'])
def add_category_form():
    return render_template('inventory/categories/add_category.html')

# הוספת קטגוריה בפועל
@category_routes.route('/categories/add', methods=['POST'])
def add_category():
    name = request.form['name']
    description = request.form.get('description', '')
    category_controller.create_category(name, description)
    return redirect(url_for('category_routes.list_categories'))

# טופס עריכה לקטגוריה
@category_routes.route('/categories/edit/<int:id>', methods=['GET'])
def edit_category_form(id):
    category = category_controller.get_category(id)
    return render_template('inventory/categories/edit_category.html', category=category)

# עדכון קטגוריה בפועל
@category_routes.route('/categories/edit/<int:id>', methods=['POST'])
def edit_category(id):
    fields = {
        'name': request.form['name'],
        'description': request.form.get('description', '')
    }
    category_controller.update_category(id, fields)
    return redirect(url_for('category_routes.list_categories'))

# מחיקת קטגוריה
@category_routes.route('/categories/delete/<int:id>', methods=['POST'])
def delete_category(id):
    category_controller.delete_category(id)
    return redirect(url_for('category_routes.list_categories'))
