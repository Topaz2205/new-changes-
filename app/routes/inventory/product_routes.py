from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, make_response
from app.controllers.inventory.product_controller import ProductController
from app.controllers.inventory.category_controller import CategoryController
from app.controllers.inventory.supplier_controller import SupplierController
from app.controllers.inventory.product_color_controller import ColorController
from app.controllers.inventory.inventory_controller import InventoryController
from app.DB.db import get_db_connection
from app.models.models_inventory.product import Product
from datetime import datetime

# Blueprint להגדרת קבוצת ראוטים של מוצרים
# template_folder כאן משמש בהתאמה למבנה התיקיות שלך (app/templates/...)
product_routes = Blueprint('product_routes', __name__, template_folder='../../templates')

# בקרים (Controllers) לשכבת הלוגיקה/DB
product_controller = ProductController()
category_controller = CategoryController()
supplier_controller = SupplierController()
color_controller = ColorController()
inventory_controller = InventoryController()
# ----------------------------
# רשימת מוצרים
# ----------------------------
@product_routes.route('/products')
def list_products():
    products = product_controller.get_all_products()
    # שים לב: הנתיב לתבנית תואם למבנה שלך app/templates/inventory/products/product.html
    return render_template('inventory/products/product.html', products=products)


# ----------------------------
# טופס הוספת מוצר
# ----------------------------
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

# ----------------------------
# הוספת מוצר בפועל
# ----------------------------
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
    flash('המוצר נוסף בהצלחה', 'success')
    return redirect(url_for('product_routes.list_products'))


@product_routes.route('/products/<int:product_id>/stock/add', methods=['GET'])
def add_stock_partial(product_id):
    # טוען את הטופס למודאל (HTMX)
    product = product_controller.get_product(product_id)
    if not product:
        abort(404)
    return render_template('inventory/products/_add_stock_partial.html', product=product)
# ----------------------------
# טופס עריכת מוצר
# ----------------------------
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

# ----------------------------
# עדכון מוצר בפועל
# ----------------------------
@product_routes.route('/products/edit/<int:id>', methods=['POST'])
def edit_product(id):
    updates = {
        'name': request.form['name'],
        'supplier_id': int(request.form['supplier_id']),
        'category_id': int(request.form['category_id']),
        'quantity_per_unit': request.form.get('quantity_per_unit', ''),
        'color_id': int(request.form.get('color_id')) if request.form.get('color_id') else None,
        # תיקון: המפתח צריך להיות unit_price (לא price)
        'unit_price': float(request.form['unit_price']),
        'units_in_stock': int(request.form.get('units_in_stock', 0)),
        'description': request.form.get('description', ''),
        'image_url': request.form.get('image_url', ''),
        'discontinued': bool(int(request.form.get('discontinued', 0)))
    }
    product_controller.update_product(id, updates)
    flash('המוצר עודכן בהצלחה', 'success')
    return redirect(url_for('product_routes.list_products'))

# ----------------------------
# מחיקת מוצר
# ----------------------------
@product_routes.route('/products/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product_controller.delete_product(id)
    flash('המוצר נמחק בהצלחה', 'success')
    return redirect(url_for('product_routes.list_products'))

# ============================================================
# HTMX — הוספת מלאי מהירה (Modal Partial + פעולה)
# ============================================================

# מחזיר Partial שמוזרק למודל (טופס להזנת כמות)
@product_routes.route('/products/<int:product_id>/stock/add', methods=['POST'])
def add_stock(product_id):
    try:
        amount = int(request.form.get('amount', 0))
    except (TypeError, ValueError):
        amount = 0

    if amount <= 0:
        flash("כמות חייבת להיות גדולה מאפס", "error")
        # אם הגיע דרך HTMX - נבצע Redirect צד לקוח
        if 'HX-Request' in request.headers:
            resp = make_response('', 204)
            resp.headers['HX-Redirect'] = url_for('product_routes.list_products')
            return resp
        return redirect(url_for('product_routes.list_products'))

# 1) מקור אמת: Inventory
    inventory_controller.add_stock(product_id, amount)

    flash("המלאי עודכן בהצלחה", "success")

    # תמיכה ב-HTMX: נבקש מהדפדפן לטעון מחדש את רשימת המוצרים
    if 'HX-Request' in request.headers:
        resp = make_response('', 204)
        resp.headers['HX-Redirect'] = url_for('product_routes.list_products')
        return resp

    return redirect(url_for('product_routes.list_products'))

