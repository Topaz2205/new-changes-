from flask import Blueprint, render_template, request, redirect, url_for, abort, render_template_string
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

        # עדכון סטטוס בבסיס הנתונים
        controller.update_order_status(order_id, new_status, delay_reason=delay_reason)

        # אם זה מגיע מ-HTMX – מחזירים את תא הסטטוס המעודכן בלבד
        if request.headers.get("HX-Request") == "true":
            # שלוף את ההזמנה המעודכנת (התאם לשם הפונקציה אצלך)
            order = controller.get_order_by_id(order_id)

            # מחזירים את תוכן ה-<td> בדיוק כמו ב-list.html
            td_tpl = """
<td id="status-cell-{{ order.order_id }}" class="status-col align-middle text-nowrap">
  {% set s = (order.status or '')|upper %}
  {% set color = 'secondary' %}
  {% if s == 'NEW' %}{% set color = 'info' %}
  {% elif s == 'PAID' %}{% set color = 'primary' %}
  {% elif s == 'SHIPPED' %}{% set color = 'warning' %}
  {% elif s == 'DELIVERED' %}{% set color = 'success' %}
  {% elif s in ['CANCELLED','CANCELED'] %}{% set color = 'danger' %}
  {% endif %}

  <span class="badge bg-{{ color }} me-2">{{ s or 'לא ידוע' }}</span>

  <form method="POST"
        action="{{ url_for('orders.set_status', order_id=order.order_id) }}"
        class="d-inline-flex align-items-center gap-2"
        hx-post="{{ url_for('orders.set_status', order_id=order.order_id) }}"
        hx-target="#status-cell-{{ order.order_id }}"
        hx-swap="outerHTML">
    <select name="status" required class="form-select form-select-sm" style="max-width:10rem;">
      <option value="NEW"       {{ 'selected' if s == 'NEW' else '' }}>NEW</option>
      <option value="PAID"      {{ 'selected' if s == 'PAID' else '' }}>PAID</option>
      <option value="SHIPPED"   {{ 'selected' if s == 'SHIPPED' else '' }}>SHIPPED</option>
      <option value="DELIVERED" {{ 'selected' if s == 'DELIVERED' else '' }}>DELIVERED</option>
      <option value="CANCELLED" {{ 'selected' if s in ['CANCELLED','CANCELED'] else '' }}>CANCELLED</option>
    </select>

    <input type="text" name="delay_reason" placeholder="סיבת עיכוב (לא חובה)"
           class="form-control form-control-sm" style="max-width:14rem;">
    <button type="submit" class="btn btn-sm btn-primary">עדכן</button>
  </form>
</td>
"""
            return render_template_string(td_tpl, order=order)

        # בקשה רגילה (לא HTMX): חזרה לרשימת ההזמנות
        return redirect(url_for("orders.list_orders"))

    except ValueError as e:
        return str(e), 400
