from app.controllers.orders.customer_controller import CustomerController
from app.controllers.orders.order_controller import OrderController
from app.controllers.orders.shipments_controller import ShipmentController
from app.controllers.orders.delivery_status_controller import DeliveryStatusController  # ← חדש
from app.models.models_access.user import User
from app.controllers.orders.shippers_controller import ShipperController
from app.controllers.orders.order_details_controller import OrderDetailsController  # ← חדש


class OrderService:
    def __init__(self):
        self.customer_controller = CustomerController()
        self.order_controller = OrderController()
        self.shipment_controller = ShipmentController()
        self.delivery_status_controller = DeliveryStatusController() 
        self.shippers_controller = ShipperController()
        self.order_details_controller = OrderDetailsController()  # ← חדש

 # ← חדש

    # ----------------------------------------
    # בקרת הרשאות לפי תפקיד
    # ----------------------------------------
    def _check_permission(self, user: User, allowed_roles):
        if user.role not in allowed_roles:
            raise PermissionError(f"{user.role} is not authorized for this action")

    # ----------------------------------------
    # פעולות על לקוחות
    # ----------------------------------------
    def create_customer(self, customer_data):
        self.customer_controller.create_customer(customer_data)

    def update_customer(self, customer_id, updated_data):
        self.customer_controller.update_customer(customer_id, updated_data)

    def delete_customer(self, customer_id):
        self.customer_controller.delete_customer(customer_id)

    def get_customer_orders(self, customer_id, user: User):
        self._check_permission(user, ["Sales Manager", "Customer Service"])
        return self.customer_controller.get_customer_orders(customer_id)

    # ----------------------------------------
    # פעולות על הזמנות
    # ----------------------------------------
    def create_order(self, order_data, user: User):
        self._check_permission(user, ["Sales Manager", "Customer Service"])
        return self.order_controller.create_order(**order_data)

    def get_order(self, order_id, user: User):
        self._check_permission(user, ["Sales Manager", "Customer Service", "Admin"])
        return self.order_controller.get_order_by_id(order_id)

    def list_orders(self, user: User):
        self._check_permission(user, ["Sales Manager", "Admin"])
        return self.order_controller.get_all_orders()

    def update_order_status(self, order_id, new_status, user: User):
        self._check_permission(user, ["Sales Manager"])
        self.order_controller.update_order_status(order_id, new_status)

    def delete_order(self, order_id, user: User):
        self._check_permission(user, ["Admin"])
        self.order_controller.delete_order(order_id)

    def update_order_details(self, order_id, fields, user: User):
        self._check_permission(user, ["Sales Manager", "Admin"])
        self.order_controller.update_order_details(order_id, fields)

    def get_orders_by_customer(self, customer_id, user: User):
        self._check_permission(user, ["Sales Manager", "Customer Service"])
        return self.order_controller.get_orders_by_customer(customer_id)

    def get_orders_by_status(self, status, user: User):
        self._check_permission(user, ["Sales Manager", "Admin"])
        return self.order_controller.get_orders_by_status(status)

    def mark_as_shipped(self, order_id, user: User):
        self._check_permission(user, ["Sales Manager"])
        self.order_controller.mark_order_as_shipped(order_id)

    def mark_as_delivered(self, order_id, user: User):
        self._check_permission(user, ["Sales Manager", "Customer Service"])
        self.order_controller.mark_order_as_delivered(order_id)

    # ----------------------------------------
    # פעולות על משלוחים
    # ----------------------------------------
    def create_shipment(self, shipment_data, user: User):
        self._check_permission(user, ["Sales Manager"])
        return self.shipment_controller.create_shipment(**shipment_data)

    def get_shipment(self, shipment_id, user: User):
        self._check_permission(user, ["Sales Manager", "Customer Service"])
        return self.shipment_controller.get_shipment_by_id(shipment_id)

    def get_shipments_by_order(self, order_id, user: User):
        self._check_permission(user, ["Sales Manager", "Customer Service"])
        return self.shipment_controller.get_shipments_by_order(order_id)

    def update_shipment_status(self, shipment_id, new_status, user: User):
        self._check_permission(user, ["Sales Manager"])
        return self.shipment_controller.update_status(shipment_id, new_status)

    # ----------------------------------------
    # סטטוס משלוח (DeliveryStatus)
    # ----------------------------------------
    def update_delivery_status(self, order_id, new_status, delay_reason, user: User):
        self._check_permission(user, ["Customer Service", "Sales Manager"])
        self.delivery_status_controller.update_status(order_id, new_status, delay_reason)

    def get_delivery_status(self, order_id, user: User):
        self._check_permission(user, ["Customer Service", "Sales Manager", "Admin"])
        return self.delivery_status_controller.get_status_by_order(order_id)

    # פעולות על מובילים (Shippers)
    # ----------------------------------------
    def register_shipper(self, company_name, phone, user: User):
        self._check_permission(user, ["Admin", "Sales Manager"])
        return self.shipper_controller.register_shipper(company_name, phone)

    def get_all_shippers(self, user: User):
        self._check_permission(user, ["Admin", "Sales Manager", "Customer Service"])
        return self.shipper_controller.get_all_shippers()

    def get_shipper_by_id(self, shipper_id, user: User):
        self._check_permission(user, ["Admin", "Sales Manager", "Customer Service"])
        return self.shipper_controller.get_shipper_by_id(shipper_id)
    
    # ----------------------------------------
    # פרטי הזמנה
    # ----------------------------------------
    def add_order_detail(self, detail_data, user: User):
        self._check_permission(user, ["Sales Manager", "Customer Service"])
        self.order_details_controller.add_order_detail(**detail_data)

    def get_order_details(self, order_id, user: User):
        self._check_permission(user, ["Sales Manager", "Customer Service"])
        return self.order_details_controller.get_details_by_order(order_id)

    def delete_order_detail(self, detail_id, user: User):
        self._check_permission(user, ["Sales Manager", "Admin"])
        self.order_details_controller.delete_order_detail(detail_id)

    def generate_sales_report(self, start_date, end_date, user: User):
        self._check_permission(user, ["Sales Manager", "Admin"])
        return self.order_controller.generate_sales_report(start_date, end_date)
