from flask import Blueprint, render_template, request, redirect, url_for, abort
from datetime import datetime
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
        try:
            user_id = int(request.form.get("user_id"))
            customer_id = int(request.form.get("customer_id"))
            employee_id = int(request.form.get("employee_id")) if request.form.get("employee_id") else None

            # normalize status to UPPER for the DB CHECK
            status_raw = request.form.get("status") or "NEW"
            status = status_raw.strip().upper()

            ship_via = request.form.get("ship_via")
            freight = float(request.form.get("freight")) if request.form.get("freight") else 0.0
            total_amount = float(request.form.get("total_amount")) if request.form.get("total_amount") else 0.0

            # dates
            fmt = "%Y-%m-%d"
            expected_delivery = request.form.get("expected_delivery") or None
            actual_delivery   = request.form.get("actual_delivery") or None
            shipped_date      = request.form.get("shipped_date") or None

            if expected_delivery:
                expected_delivery = datetime.strptime(expected_delivery, fmt)
            if actual_delivery:
                actual_delivery = datetime.strptime(actual_delivery, fmt)
            if shipped_date:
                shipped_date = datetime.strptime(shipped_date, fmt)

            controller.create_order(
                user_id, customer_id, employee_id, status, ship_via,
                freight, total_amount, expected_delivery, actual_delivery, shipped_date
            )
            return redirect(url_for("orders.list_orders"))

        except ValueError as e:
            # למשל אם סטטוס לא חוקי – הוולידציה בקונטרולר תזרוק ValueError
            return str(e), 400

    return render_template("orders/create.html")

@order_routes.route('/edit/<int:order_id>', methods=['GET', 'POST'])
@login_required
@permission_required("manage_orders")
def edit_order(order_id):
    order = controller.get_order_by_id(order_id)
    if not order:
        abort(404)

    if request.method == 'POST':
        try:
            fields = {
                'status': (request.form.get('status') or '').strip().upper() if request.form.get('status') else None,
                'employee_id': int(request.form.get('employee_id')) if request.form.get('employee_id') else None,
                'freight': float(request.form.get('freight')) if request.form.get('freight') else None,
                'total_amount': float(request.form.get('total_amount')) if request.form.get('total_amount') else None,
            }

            # תאריכים – המרה מפורמט string ל־datetime אם קיים ערך
            for field in ['shipped_date', 'expected_delivery', 'actual_delivery']:
                date_str = request.form.get(field)
                if date_str:
                    try:
                        fields[field] = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
                    except ValueError:
                        fields[field] = None  # אפשר גם להשאיר את הישן/להחזיר שגיאה לפי UX

            controller.update_order_details(order_id, fields)
            return redirect(url_for('orders.list_orders'))

        except ValueError as e:
            return str(e), 400

    return render_template('orders/edit_order.html', order=order)

# === Route ייעודי לעדכון סטטוס + סיבה לעיכוב (אופציונלי) ===
@order_routes.route("/<int:order_id>/status", methods=["POST"])
@login_required
@permission_required("manage_orders")
def set_status(order_id):
    try:
        new_status = (request.form.get("status") or "").strip().upper()
        delay_reason = request.form.get("delay_reason") or None
        controller.update_order_status(order_id, new_status, delay_reason=delay_reason)
        return redirect(url_for("orders.list_orders"))
    except ValueError as e:
        return str(e), 400
