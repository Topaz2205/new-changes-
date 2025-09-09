from flask import Blueprint, render_template, request, redirect, url_for
from app.controllers.orders.order_controller import OrderController
from app.utils.decorators import login_required, permission_required  


order_routes = Blueprint("orders", __name__, url_prefix="/orders")
controller = OrderController()

@order_routes.route("/")
@login_required
@permission_required("view_orders")
def list_orders():
    orders = controller.get_all_orders()
    return render_template("orders/list.html", orders=orders)

@order_routes.route("/create", methods=["GET", "POST"])
@login_required
@permission_required("manage_orders")
def create_order():
    if request.method == "POST":
        user_id = int(request.form.get("user_id"))
        customer_id = int(request.form.get("customer_id"))
        employee_id = int(request.form.get("employee_id"))
        status = request.form.get("status")
        ship_via = request.form.get("ship_via")
        freight = float(request.form.get("freight"))
        total_amount = float(request.form.get("total_amount"))
        expected_delivery = request.form.get("expected_delivery") or None
        actual_delivery = request.form.get("actual_delivery") or None
        shipped_date = request.form.get("shipped_date") or None

        # הפוך תאריכים למבנה datetime אם יש ערכים
        from datetime import datetime
        fmt = "%Y-%m-%d"
        if expected_delivery:
            expected_delivery = datetime.strptime(expected_delivery, fmt)
        if actual_delivery:
            actual_delivery = datetime.strptime(actual_delivery, fmt)
        if shipped_date:
            shipped_date = datetime.strptime(shipped_date, fmt)

        # קריאה לפונקציה בקונטרולר
        controller.create_order(
            user_id, customer_id, employee_id, status, ship_via,
            freight, total_amount, expected_delivery, actual_delivery, shipped_date
        )

        return redirect(url_for("orders.list_orders"))

    return render_template("orders/create.html")

from datetime import datetime

@order_routes.route('/edit/<int:order_id>', methods=['GET', 'POST'])
@login_required
def edit_order(order_id):
    order = controller.get_order_by_id(order_id)

    if request.method == 'POST':
        fields = {
            'status': request.form.get('status'),
            'employee_id': request.form.get('employee_id'),
            'freight': request.form.get('freight'),
            'total_amount': request.form.get('total_amount'),
        }

        # המרה ל-int/float אם יש ערך
        if fields['employee_id']:
            fields['employee_id'] = int(fields['employee_id'])

        if fields['freight']:
            fields['freight'] = float(fields['freight'])

        if fields['total_amount']:
            fields['total_amount'] = float(fields['total_amount'])

        # תאריכים – המרה מפורמט string ל־datetime אם קיים ערך
        date_fields = ['shipped_date', 'expected_delivery', 'actual_delivery']
        for field in date_fields:
            date_str = request.form.get(field)
            if date_str:
                try:
                    fields[field] = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    fields[field] = None  # או טיפול אחר במקרה של תאריך לא תקין

        controller.update_order_details(order_id, fields)
        return redirect(url_for('orders.list_orders'))

    return render_template('orders/edit_order.html', order=order)
