from flask import Blueprint, render_template, request, redirect, url_for
from app.controllers.inventory.product_controller import ProductController
from app.controllers.inventory.category_controller import CategoryController
from app.controllers.inventory.supplier_controller import SupplierController
from app.controllers.inventory.product_color_controller import ColorController
from app.models.models_inventory.product import Product
from datetime import datetime

product_routes = Blueprint('product_routes', __name__, template_folder='../../templates')

product_controller = ProductController()
category_controller = CategoryController()
supplier_controller = SupplierController()
color_controller = ColorController()

# הצגת כל המוצרים
@product_routes.route('/products')
def list_products():
    products = product_controller.get_all_products()
    return render_template('inventory/products/product.html', products=products)

# טופס להוספת מוצר חדש
@product_routes.route('/products/add', methods=['GET'])
def add_product_form():
    categories = category_controller.get_all_categories()
    suppliers = supplier_controller.get_all_suppliers()
    colors = color_controller.get_all_colors()
    return render_template(
        'inventory/products/add_product.html',
        categories=categories,
        suppliers=suppliers,
        colors=colors
    )

# הוספת מוצר בפועל
@product_routes.route('/products/add', methods=['POST'])
def add_product():
    product = Product(
        id=None,
        name=request.form['name'],
        supplier_id=int(request.form['supplier_id']),
        category_id=int(request.form['category_id']),
        quantity_per_unit=request.form.get('quantity_per_unit', ''),
        color_id=int(request.form.get('color_id')) if request.form.get('color_id') else None,
        unit_price=float(request.form['unit_price']),
        units_in_stock=int(request.form.get('units_in_stock', 0)),
        description=request.form.get('description', ''),
        image_url=request.form.get('image_url', ''),
        discontinued=bool(int(request.form.get('discontinued', 0)))
    )
    product_controller.create_product(product)
    return redirect(url_for('product_routes.list_products'))

# טופס עריכה
@product_routes.route('/products/edit/<int:id>', methods=['GET'])
def edit_product_form(id):
    product = product_controller.get_product(id)
    categories = category_controller.get_all_categories()
    suppliers = supplier_controller.get_all_suppliers()
    colors = color_controller.get_all_colors()
    return render_template(
        'inventory/products/edit_product.html',
        product=product,
        categories=categories,
        suppliers=suppliers,
        colors=colors
    )

# עדכון בפועל
@product_routes.route('/products/edit/<int:id>', methods=['POST'])
def edit_product(id):
    updates = {
        'name': request.form['name'],
        'supplier_id': int(request.form['supplier_id']),
        'category_id': int(request.form['category_id']),
        'quantity_per_unit': request.form.get('quantity_per_unit', ''),
        'color_id': int(request.form.get('color_id')) if request.form.get('color_id') else None,
        'price': float(request.form['unit_price']),
        'units_in_stock': int(request.form.get('units_in_stock', 0)),
        'description': request.form.get('description', ''),
        'image_url': request.form.get('image_url', ''),
        'discontinued': bool(int(request.form.get('discontinued', 0)))
    }
    product_controller.update_product(id, updates)
    return redirect(url_for('product_routes.list_products'))

# מחיקת מוצר
@product_routes.route('/products/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product_controller.delete_product(id)
    return redirect(url_for('product_routes.list_products'))
