from flask import Blueprint, render_template, request, redirect, url_for
from app.controllers.inventory.supplier_controller import SupplierController
from app.models.models_inventory.supplier import Supplier

supplier_routes = Blueprint('supplier_routes', __name__, template_folder='../../templates')
supplier_controller = SupplierController()

# הצגת כל הספקים
@supplier_routes.route('/suppliers')
def list_suppliers():
    suppliers = supplier_controller.get_all_suppliers()
    return render_template('inventory/suppliers/supplier.html', suppliers=suppliers)

# טופס להוספת ספק חדש
@supplier_routes.route('/suppliers/add', methods=['GET'])
def add_supplier_form():
    return render_template('inventory/suppliers/add_supplier.html')

# הוספת ספק בפועל
@supplier_routes.route('/suppliers/add', methods=['POST'])
def add_supplier():
    supplier = Supplier(
        id=None,
        company_name=request.form['company_name'],
        contact_name=request.form.get('contact_name', ''),
        contact_email=request.form.get('contact_email', ''),
        address=request.form.get('address', ''),
        city=request.form.get('city', ''),
        country=request.form.get('country', ''),
        phone=request.form.get('phone', '')
    )
    supplier_controller.create_supplier(supplier)
    return redirect(url_for('supplier_routes.list_suppliers'))

# טופס עריכה
@supplier_routes.route('/suppliers/edit/<int:id>', methods=['GET'])
def edit_supplier_form(id):
    supplier = supplier_controller.get_supplier_by_id(id)
    return render_template('inventory/suppliers/edit_supplier.html', supplier=supplier)

# עדכון בפועל
@supplier_routes.route('/suppliers/edit/<int:id>', methods=['POST'])
def edit_supplier(id):
    updated_data = {
        'company_name': request.form['company_name'],
        'contact_name': request.form.get('contact_name', ''),
        'contact_email': request.form.get('contact_email', ''),
        'address': request.form.get('address', ''),
        'city': request.form.get('city', ''),
        'country': request.form.get('country', ''),
        'phone': request.form.get('phone', '')
    }
    supplier_controller.update_supplier(id, updated_data)
    return redirect(url_for('supplier_routes.list_suppliers'))

# מחיקה
@supplier_routes.route('/suppliers/delete/<int:id>', methods=['POST'])
def delete_supplier(id):
    supplier_controller.delete_supplier(id)
    return redirect(url_for('supplier_routes.list_suppliers'))
