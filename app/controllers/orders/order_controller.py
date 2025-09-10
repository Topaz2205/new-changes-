from datetime import datetime
from app.DB.db import get_db_connection
from app.models.models_orders.order import Order
from app.controllers.orders.delivery_status_controller import DeliveryStatusController

# סטטוסים מותרים לפי ה-CHECK שבסכימה
ALLOWED_ORDER_STATUSES = {'NEW', 'PAID', 'SHIPPED', 'DELIVERED', 'CANCELLED'}

def _validate_order_status(status: str):
    if status not in ALLOWED_ORDER_STATUSES:
        raise ValueError(f"סטטוס לא חוקי: {status}. מותר: {sorted(ALLOWED_ORDER_STATUSES)}")

class OrderController:
    def __init__(self):
        self._delivery_status = DeliveryStatusController()

    # יצירת הזמנה חדשה
    def create_order(self, user_id, customer_id, employee_id, status, ship_via, freight, total_amount,
                     expected_delivery=None, actual_delivery=None, shipped_date=None):
        # ולידציה לפני DB
        _validate_order_status(status)

        conn = get_db_connection()
        cursor = conn.cursor()

        order_date = datetime.now()
        cursor.execute("""
            INSERT INTO Orders (
                user_id, customer_id, employee_id, order_date, shipped_date, status,
                ship_via, freight, total_amount, expected_delivery, actual_delivery
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            customer_id,
            employee_id,
            order_date,
            shipped_date,
            status,
            ship_via,
            freight,
            total_amount,
            expected_delivery,
            actual_delivery
        ))

        conn.commit()
        order_id = cursor.lastrowid
        conn.close()

        # רישום היסטוריית סטטוס להזמנה החדשה
        self._delivery_status.update_status(order_id, status, delay_reason=None)

        # שים לב: אם ה-Order(model) שלך מצפה לסדר פרמטרים אחר, עדכן בהתאם
        return Order(order_id, customer_id, employee_id, order_date, shipped_date, status,
                     ship_via, freight, total_amount, expected_delivery, actual_delivery)

    # שליפת הזמנה לפי מזהה
    def get_order_by_id(self, order_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return Order(**row)
        return None

    # שליפת כל ההזמנות
    def get_all_orders(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                O.order_id AS order_id, 
                O.customer_id, 
                O.employee_id, 
                O.order_date, 
                O.shipped_date, 
                O.status, 
                O.ship_via, 
                O.freight, 
                O.total_amount, 
                O.expected_delivery, 
                O.actual_delivery,
                Customers.contact_name AS customer_name,
                Employees.first_name || ' ' || Employees.last_name AS employee_name               
            FROM Orders as O
            LEFT JOIN Customers ON O.customer_id = Customers.customer_id
            LEFT JOIN Employees ON O.employee_id = Employees.id
        """)
        rows = cursor.fetchall()
        conn.close()

        orders = []
        for row in rows:
            row = dict(row)
            # המרת תאריכים אם יש
            for field in ['order_date', 'shipped_date', 'expected_delivery', 'actual_delivery']:
                if row.get(field):
                    try:
                        row[field] = datetime.fromisoformat(row[field])
                    except Exception:
                        pass
            orders.append(row)

        return orders

    # עדכון סטטוס להזמנה (כולל היסטוריה)
    def update_order_status(self, order_id, new_status, delay_reason=None):
        _validate_order_status(new_status)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Orders SET status = ?, updated_at = ?
            WHERE order_id = ?
        """, (new_status, datetime.now(), order_id))
        conn.commit()
        conn.close()

        # רישום היסטוריה
        self._delivery_status.update_status(order_id, new_status, delay_reason=delay_reason)

    # מחיקת הזמנה
    def delete_order(self, order_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Orders WHERE order_id = ?", (order_id,))
        conn.commit()
        conn.close()

    # עדכון פרטי הזמנה נוספים (אם כולל status – נוודא ולידציה ונרשום היסטוריה)
    def update_order_details(self, order_id, fields: dict):
        allowed_fields = [
            "employee_id", "shipped_date", "ship_via", "freight", "status",
            "expected_delivery", "actual_delivery", "total_amount"
        ]

        # אם מעדכנים סטטוס—ולידציה מראש
        if "status" in fields and fields["status"] is not None:
            _validate_order_status(fields["status"])

        set_clause_parts = []
        values = []
        for key in allowed_fields:
            if key in fields:
                set_clause_parts.append(f"{key} = ?")
                values.append(fields[key])

        if not set_clause_parts:
            return

        set_clause = ", ".join(set_clause_parts)
        values.append(datetime.now())  # updated_at
        values.append(order_id)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE Orders SET {set_clause}, updated_at = ? WHERE order_id = ?
        """, values)
        conn.commit()
        conn.close()

        # אם עודכן סטטוס—גם היסטוריה
        if "status" in fields and fields["status"] is not None:
            self._delivery_status.update_status(order_id, fields["status"], delay_reason=None)

    # שליפת הזמנות לפי לקוח
    def get_orders_by_customer(self, customer_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Orders WHERE customer_id = ?", (customer_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Order(**row).to_dict() for row in rows]

    # שליפת הזמנות לפי סטטוס
    def get_orders_by_status(self, status):
        _validate_order_status(status)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Orders WHERE status = ?", (status,))
        rows = cursor.fetchall()
        conn.close()
        return [Order(**row).to_dict() for row in rows]

    # סימון הזמנה כמשלוח
    def mark_order_as_shipped(self, order_id):
        shipped_date = datetime.now()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Orders
            SET status = 'SHIPPED', shipped_date = ?, updated_at = ?
            WHERE order_id = ?
        """, (shipped_date, shipped_date, order_id))
        conn.commit()
        conn.close()
        # היסטוריה
        self._delivery_status.update_status(order_id, 'SHIPPED', delay_reason=None)

    # סימון הזמנה כנמסרה
    def mark_order_as_delivered(self, order_id):
        delivery_date = datetime.now()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Orders
            SET status = 'DELIVERED', actual_delivery = ?, updated_at = ?
            WHERE order_id = ?
        """, (delivery_date, delivery_date, order_id))
        conn.commit()
        conn.close()
        # היסטוריה
        self._delivery_status.update_status(order_id, 'DELIVERED', delay_reason=None)

    # דו"ח מכירות לפי טווח תאריכים
    def generate_sales_report(self, start_date, end_date):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT status, COUNT(*) as total_orders, SUM(total_amount) as total_revenue
            FROM Orders
            WHERE order_date BETWEEN ? AND ?
            GROUP BY status
        """, (start_date, end_date))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
