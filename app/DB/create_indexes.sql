-- ===== ORDERS =====
CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON Orders(customer_id, order_date DESC);
CREATE INDEX IF NOT EXISTS idx_orders_employee      ON Orders(employee_id);
CREATE INDEX IF NOT EXISTS idx_orders_user          ON Orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status        ON Orders(status);

-- ===== ORDER ITEMS =====
CREATE INDEX IF NOT EXISTS idx_orderitems_order     ON OrderItems(order_id);
CREATE INDEX IF NOT EXISTS idx_orderitems_product   ON OrderItems(product_id);

-- ===== PRODUCTS =====
CREATE INDEX IF NOT EXISTS idx_products_category    ON Products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_supplier    ON Products(supplier_id);
CREATE INDEX IF NOT EXISTS idx_products_color       ON Products(color_id);
CREATE INDEX IF NOT EXISTS idx_products_name        ON Products(name);

-- ===== INVENTORY HISTORY =====
CREATE INDEX IF NOT EXISTS idx_inventoryhist_prod_time ON InventoryHistory(product_id, timestamp DESC);

-- ===== SHIPMENTS / DELIVERY STATUS =====
CREATE INDEX IF NOT EXISTS idx_shipments_order      ON Shipments(order_id);
CREATE INDEX IF NOT EXISTS idx_deliverystatus_order ON DeliveryStatus(order_id);

-- ===== CUSTOMERS / EMPLOYEES / USERS =====
CREATE INDEX IF NOT EXISTS idx_customers_phone      ON Customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_email      ON Customers(email);
CREATE INDEX IF NOT EXISTS idx_users_role           ON Users(role_id);
CREATE INDEX IF NOT EXISTS idx_rolepermissions_role ON RolePermissions(role_id);

-- ===== SUPPLIER INVENTORY =====
CREATE INDEX IF NOT EXISTS idx_supplierinventory_supplier ON SupplierInventory(supplier_id);
CREATE INDEX IF NOT EXISTS idx_supplierinventory_product  ON SupplierInventory(product_id);
