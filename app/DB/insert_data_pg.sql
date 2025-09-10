-- ===== ROLES =====
INSERT INTO roles (name) VALUES
  ('Admin'), ('SalesManager'), ('WarehouseManager'), ('CustomerService'), ('User')
ON CONFLICT (name) DO NOTHING;

-- ===== PERMISSIONS =====
INSERT INTO permissions (name) VALUES
  ('view_inventory'), ('manage_inventory'),
  ('view_orders'),    ('manage_orders'),
  ('view_users'),     ('manage_users')
ON CONFLICT (name) DO NOTHING;

-- ===== USERS =====
INSERT INTO users (username, email, password, role_id)
VALUES
  ('admin',      'admin@example.com',      'adminpass',    (SELECT id FROM roles WHERE name='Admin')),
  ('sales1',     'sales1@example.com',     'salespass',    (SELECT id FROM roles WHERE name='SalesManager')),
  ('warehouse1', 'warehouse1@example.com', 'warehousepass',(SELECT id FROM roles WHERE name='WarehouseManager')),
  ('support1',   'support1@example.com',   'supportpass',  (SELECT id FROM roles WHERE name='CustomerService')),
  ('user1',      'user1@example.com',      'userpass',     (SELECT id FROM roles WHERE name='User'))
ON CONFLICT (username) DO NOTHING;

-- ===== ROLE PERMISSIONS =====
-- Admin: all
INSERT INTO rolepermissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON p.name IN ('manage_users','view_users','view_orders','manage_orders','view_inventory','manage_inventory')
WHERE r.name = 'Admin'
ON CONFLICT DO NOTHING;

-- SalesManager: orders (view+manage)
INSERT INTO rolepermissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON p.name IN ('view_orders','manage_orders')
WHERE r.name = 'SalesManager'
ON CONFLICT DO NOTHING;

-- WarehouseManager: inventory (view+manage)
INSERT INTO rolepermissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON p.name IN ('view_inventory','manage_inventory')
WHERE r.name = 'WarehouseManager'
ON CONFLICT DO NOTHING;

-- CustomerService: orders (view+manage)
INSERT INTO rolepermissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON p.name IN ('view_orders','manage_orders')
WHERE r.name = 'CustomerService'
ON CONFLICT DO NOTHING;

-- User: minimal views
INSERT INTO rolepermissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON p.name IN ('view_orders','view_inventory')
WHERE r.name = 'User'
ON CONFLICT DO NOTHING;

-- ===== SUPPLIERS =====  (בסכמה שלך suppliers כולל רק company_name)
INSERT INTO suppliers (company_name) VALUES
  ('Sanifix Ltd.'), ('AquaPro Systems'), ('Nir Faucets'), ('PlumbLine'), ('HydroFlow'),
  ('TapTech'), ('FlowFix'), ('DripMaster'), ('AquaPro Elite'), ('SanitaryPro')
ON CONFLICT DO NOTHING;

-- ===== CATEGORIES =====
INSERT INTO categories (name) VALUES
  ('ברזים'),
  ('כיורים'),
  ('אסלות'),
  ('אמבטיות'),
  ('מקלחונים'),
  ('ארונות אמבטיה'),
  ('ברזי מטבח'),
  ('אביזרי תלייה'),
  ('ניאגרות'),
  ('כלים לאינסטלציה')
ON CONFLICT (name) DO NOTHING;

-- ===== PRODUCT COLORS =====
-- בסכמה שלך: productcolors(color_name, hex_code)
INSERT INTO productcolors (color_name, hex_code) VALUES
  ('כרום',            '#C0C0C0'),
  ('כסוף',            '#C0C0C0'),
  ('לבן',             '#FFFFFF'),
  ('שחור מט',         '#1C1C1C'),
  ('נירוסטה',         '#B0B0B0'),
  ('ניקל מוברש',      '#D3D3D3'),
  ('נירוסטה מבריקה',  '#A9A9A9')
ON CONFLICT DO NOTHING;

-- ===== PRODUCTS =====
-- אין UNIQUE על products.name אצלך, לכן נכניס בצורה ממוגנת כפילות (WHERE NOT EXISTS)
INSERT INTO products (name, supplier_id, category_id, quantity_per_unit, color_id, price, discontinued)
SELECT 'ברז מטבח נשלף',
       (SELECT id FROM suppliers WHERE company_name='Sanifix Ltd.'),
       (SELECT id FROM categories WHERE name='ברזים'),
       '1 יחידה',
       (SELECT id FROM productcolors WHERE color_name='כרום'),
       349.90, FALSE
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name='ברז מטבח נשלף');

INSERT INTO products (name, supplier_id, category_id, quantity_per_unit, color_id, price, discontinued)
SELECT 'ראש טוש עגול',
       (SELECT id FROM suppliers WHERE company_name='AquaPro Systems'),
       (SELECT id FROM categories WHERE name='מקלחונים'),
       '1 יחידה',
       (SELECT id FROM productcolors WHERE color_name='כסוף'),
       199.00, FALSE
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name='ראש טוש עגול');

INSERT INTO products (name, supplier_id, category_id, quantity_per_unit, color_id, price, discontinued)
SELECT 'כיור מונח עגול',
       (SELECT id FROM suppliers WHERE company_name='Nir Faucets'),
       (SELECT id FROM categories WHERE name='כיורים'),
       '1 יחידה',
       (SELECT id FROM productcolors WHERE color_name='לבן'),
       450.00, FALSE
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name='כיור מונח עגול');

INSERT INTO products (name, supplier_id, category_id, quantity_per_unit, color_id, price, discontinued)
SELECT 'ברז אמבטיה קיר',
       (SELECT id FROM suppliers WHERE company_name='Sanifix Ltd.'),
       (SELECT id FROM categories WHERE name='ברזים'),
       '1 יחידה',
       (SELECT id FROM productcolors WHERE color_name='שחור מט'),
       599.00, FALSE
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name='ברז אמבטיה קיר');

INSERT INTO products (name, supplier_id, category_id, quantity_per_unit, color_id, price, discontinued)
SELECT 'סיפון נירוסטה',
       (SELECT id FROM suppliers WHERE company_name='FlowFix'),
       (SELECT id FROM categories WHERE name='כלים לאינסטלציה'),
       '1 יחידה',
       (SELECT id FROM productcolors WHERE color_name='נירוסטה'),
       75.00, FALSE
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name='סיפון נירוסטה');

INSERT INTO products (name, supplier_id, category_id, quantity_per_unit, color_id, price, discontinued)
SELECT 'אסלה תלויה',
       (SELECT id FROM suppliers WHERE company_name='HydroFlow'),
       (SELECT id FROM categories WHERE name='אסלות'),
       '1 יחידה',
       (SELECT id FROM productcolors WHERE color_name='לבן'),
       1200.00, FALSE
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name='אסלה תלויה');

INSERT INTO products (name, supplier_id, category_id, quantity_per_unit, color_id, price, discontinued)
SELECT 'ניאגרה סמויה',
       (SELECT id FROM suppliers WHERE company_name='PlumbLine'),
       (SELECT id FROM categories WHERE name='ניאגרות'),
       '1 יחידה',
       (SELECT id FROM productcolors WHERE color_name='לבן'),
       990.00, FALSE
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name='ניאגרה סמויה');

INSERT INTO products (name, supplier_id, category_id, quantity_per_unit, color_id, price, discontinued)
SELECT 'ברז כיור נמוך',
       (SELECT id FROM suppliers WHERE company_name='Nir Faucets'),
       (SELECT id FROM categories WHERE name='ברזים'),
       '1 יחידה',
       (SELECT id FROM productcolors WHERE color_name='ניקל מוברש'),
       310.00, FALSE
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name='ברז כיור נמוך');

INSERT INTO products (name, supplier_id, category_id, quantity_per_unit, color_id, price, discontinued)
SELECT 'מראה עם תאורה',
       (SELECT id FROM suppliers WHERE company_name='DripMaster'),
       (SELECT id FROM categories WHERE name='ארונות אמבטיה'),
       '1 יחידה',
       (SELECT id FROM productcolors WHERE color_name='כסוף'),
       680.00, FALSE
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name='מראה עם תאורה');

INSERT INTO products (name, supplier_id, category_id, quantity_per_unit, color_id, price, discontinued)
SELECT 'מתלה מגבות קיר',
       (SELECT id FROM suppliers WHERE company_name='AquaPro Elite'),
       (SELECT id FROM categories WHERE name='אביזרי תלייה'),
       '1 יחידה',
       (SELECT id FROM productcolors WHERE color_name='נירוסטה מבריקה'),
       115.00, FALSE
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name='מתלה מגבות קיר');

-- ===== CUSTOMERS =====  (ללא contact_title/customer_type/customer_tag)
INSERT INTO customers (contact_name, address, city, postal_code, country, phone, email) VALUES
  ('Yossi Cohen', 'Herzl 10',     'Tel Aviv',   '61000', 'Israel', '050-1234567', 'yossi@example.com'),
  ('Dana Levi',   'HaAtzmaut 5',  'Haifa',      '32000', 'Israel', '054-9876543', 'dana@example.com'),
  ('Amit Bar',    'Weizmann 22',  'Jerusalem',  '91000', 'Israel', '052-4567890', 'amitb@example.com'),
  ('Roni Gilad',  'Ben Gurion 8', 'Ramat Gan',  '52000', 'Israel', '053-3214567', 'ronig@example.com'),
  ('Noa Avraham', 'Begin 3',      'Ashdod',     '77000', 'Israel', '054-8765432', 'noaa@example.com')
ON CONFLICT DO NOTHING;

-- ===== EMPLOYEES =====
INSERT INTO employees (user_id, first_name, last_name, position, birth_date, hire_date, address, city, postal_code, country, phone, email, manager_id)
VALUES
  ((SELECT id FROM users WHERE username='admin'),      'David', 'Levi',  'CEO',               '1980-01-01','2010-01-01','Hasharon 1','Tel Aviv','61000','Israel','0501234567','david@sanitary.com', NULL),
  ((SELECT id FROM users WHERE username='sales1'),     'Rina',  'Cohen', 'Sales Manager',     '1985-02-02','2015-03-01','Herzl 2','Haifa','32000','Israel','0502345678','rina@sanitary.com',    (SELECT id FROM employees WHERE email='david@sanitary.com')),
  ((SELECT id FROM users WHERE username='warehouse1'), 'Oren',  'Mizrahi','Warehouse Manager','1983-03-03','2014-04-01','Begin 3','Beer Sheva','84000','Israel','0503456789','oren@sanitary.com',(SELECT id FROM employees WHERE email='david@sanitary.com')),
  ((SELECT id FROM users WHERE username='support1'),   'Maya',  'Bar',   'Support Manager',   '1990-04-04','2018-05-01','Ben Yehuda 4','Jerusalem','91000','Israel','0504567890','maya@sanitary.com',(SELECT id FROM employees WHERE email='david@sanitary.com')),
  ((SELECT id FROM users WHERE username='user1'),      'Yoni',  'Katz',  'Sales Rep',         '1992-05-05','2020-06-01','HaPalmach 5','Ashdod','77000','Israel','0505678901','yoni@sanitary.com', (SELECT id FROM employees WHERE email='rina@sanitary.com'))
ON CONFLICT DO NOTHING;

-- ===== ORDERS =====
-- נכניס בלי order_id ידני; נזהה כל הזמנה אח"כ לפי (customer, user, order_date, total_amount)
INSERT INTO orders (customer_id, employee_id, user_id, status, ship_via, freight, total_amount, expected_delivery, actual_delivery, shipped_date, order_date)
SELECT
  (SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen'),
  (SELECT id FROM employees WHERE email='david@sanitary.com'),
  (SELECT id FROM users WHERE username='sales1'),
  'NEW', 'FedEx', 25.50, 300.00, '2025-07-25 00:00:00', NULL, NULL, '2025-07-17 00:00:00'
WHERE NOT EXISTS (
  SELECT 1 FROM orders o
  WHERE o.customer_id = (SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen')
    AND o.user_id     = (SELECT id FROM users WHERE username='sales1')
    AND o.order_date  = '2025-07-17 00:00:00'
    AND o.total_amount = 300.00
);

INSERT INTO orders (customer_id, employee_id, user_id, status, ship_via, freight, total_amount, expected_delivery, actual_delivery, shipped_date, order_date)
SELECT
  (SELECT customer_id FROM customers WHERE contact_name='Dana Levi'),
  (SELECT id FROM employees WHERE email='rina@sanitary.com'),
  (SELECT id FROM users WHERE username='admin'),
  'SHIPPED', 'DHL', 15.00, 450.00, '2025-07-20 00:00:00', NULL, '2025-07-18 00:00:00', '2025-07-17 00:00:00'
WHERE NOT EXISTS (
  SELECT 1 FROM orders o
  WHERE o.customer_id = (SELECT customer_id FROM customers WHERE contact_name='Dana Levi')
    AND o.user_id     = (SELECT id FROM users WHERE username='admin')
    AND o.order_date  = '2025-07-17 00:00:00'
    AND o.total_amount = 450.00
);

INSERT INTO orders (customer_id, employee_id, user_id, status, ship_via, freight, total_amount, expected_delivery, actual_delivery, shipped_date, order_date)
SELECT
  (SELECT customer_id FROM customers WHERE contact_name='Amit Bar'),
  (SELECT id FROM employees WHERE email='oren@sanitary.com'),
  (SELECT id FROM users WHERE username='warehouse1'),
  'DELIVERED', 'UPS', 12.00, 180.00, '2025-07-10 00:00:00', '2025-07-11 00:00:00', '2025-07-10 00:00:00', '2025-07-17 00:00:00'
WHERE NOT EXISTS (
  SELECT 1 FROM orders o
  WHERE o.customer_id = (SELECT customer_id FROM customers WHERE contact_name='Amit Bar')
    AND o.user_id     = (SELECT id FROM users WHERE username='warehouse1')
    AND o.order_date  = '2025-07-17 00:00:00'
    AND o.total_amount = 180.00
);

INSERT INTO orders (customer_id, employee_id, user_id, status, ship_via, freight, total_amount, expected_delivery, actual_delivery, shipped_date, order_date)
SELECT
  (SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen'),
  (SELECT id FROM employees WHERE email='maya@sanitary.com'),
  (SELECT id FROM users WHERE username='support1'),
  'NEW', 'Self Pickup', 0.00, 90.00, '2025-07-28 00:00:00', NULL, NULL, '2025-07-17 00:00:00'
WHERE NOT EXISTS (
  SELECT 1 FROM orders o
  WHERE o.customer_id = (SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen')
    AND o.user_id     = (SELECT id FROM users WHERE username='support1')
    AND o.order_date  = '2025-07-17 00:00:00'
    AND o.total_amount = 90.00
);

INSERT INTO orders (customer_id, employee_id, user_id, status, ship_via, freight, total_amount, expected_delivery, actual_delivery, shipped_date, order_date)
SELECT
  (SELECT customer_id FROM customers WHERE contact_name='Noa Avraham'),
  (SELECT id FROM employees WHERE email='rina@sanitary.com'),
  (SELECT id FROM users WHERE username='admin'),
  'CANCELLED', 'GLS', 20.00, 0.00, '2025-07-30 00:00:00', NULL, NULL, '2025-07-17 00:00:00'
WHERE NOT EXISTS (
  SELECT 1 FROM orders o
  WHERE o.customer_id = (SELECT customer_id FROM customers WHERE contact_name='Noa Avraham')
    AND o.user_id     = (SELECT id FROM users WHERE username='admin')
    AND o.order_date  = '2025-07-17 00:00:00'
    AND o.total_amount = 0.00
);

-- ===== ORDER ITEMS ===== (איתור order_id לפי (customer,user,order_date,total_amount))
INSERT INTO orderitems (order_id, product_id, quantity, price_at_order)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen')
       AND o.user_id=(SELECT id FROM users WHERE username='sales1')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=300.00),
  (SELECT id FROM products WHERE name='ראש טוש עגול'),
  1, 499.99
WHERE NOT EXISTS (
  SELECT 1 FROM orderitems oi
  WHERE oi.order_id = (SELECT order_id FROM orders o
                        WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen')
                          AND o.user_id=(SELECT id FROM users WHERE username='sales1')
                          AND o.order_date='2025-07-17 00:00:00'
                          AND o.total_amount=300.00)
    AND oi.product_id = (SELECT id FROM products WHERE name='ראש טוש עגול')
);

INSERT INTO orderitems (order_id, product_id, quantity, price_at_order)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Dana Levi')
       AND o.user_id=(SELECT id FROM users WHERE username='admin')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=450.00),
  (SELECT id FROM products WHERE name='סיפון נירוסטה'),
  1, 149.99
WHERE NOT EXISTS (
  SELECT 1 FROM orderitems oi
  WHERE oi.order_id = (SELECT order_id FROM orders o
                        WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Dana Levi')
                          AND o.user_id=(SELECT id FROM users WHERE username='admin')
                          AND o.order_date='2025-07-17 00:00:00'
                          AND o.total_amount=450.00)
    AND oi.product_id = (SELECT id FROM products WHERE name='סיפון נירוסטה')
);

INSERT INTO orderitems (order_id, product_id, quantity, price_at_order)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Amit Bar')
       AND o.user_id=(SELECT id FROM users WHERE username='warehouse1')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=180.00),
  (SELECT id FROM products WHERE name='ברז אמבטיה קיר'),
  1, 89.99
WHERE NOT EXISTS (
  SELECT 1 FROM orderitems oi
  WHERE oi.order_id = (SELECT order_id FROM orders o
                        WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Amit Bar')
                          AND o.user_id=(SELECT id FROM users WHERE username='warehouse1')
                          AND o.order_date='2025-07-17 00:00:00'
                          AND o.total_amount=180.00)
    AND oi.product_id = (SELECT id FROM products WHERE name='ברז אמבטיה קיר')
);

INSERT INTO orderitems (order_id, product_id, quantity, price_at_order)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen')
       AND o.user_id=(SELECT id FROM users WHERE username='support1')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=90.00),
  (SELECT id FROM products WHERE name='כיור מונח עגול'),
  1, 199.99
WHERE NOT EXISTS (
  SELECT 1 FROM orderitems oi
  WHERE oi.order_id = (SELECT order_id FROM orders o
                        WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen')
                          AND o.user_id=(SELECT id FROM users WHERE username='support1')
                          AND o.order_date='2025-07-17 00:00:00'
                          AND o.total_amount=90.00)
    AND oi.product_id = (SELECT id FROM products WHERE name='כיור מונח עגול')
);

-- ===== ORDER UPDATES =====
INSERT INTO orderupdates (order_id, status, comment, update_type, old_value, new_value)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen')
       AND o.user_id=(SELECT id FROM users WHERE username='sales1')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=300.00),
  'SHIPPED', 'Changed status', 'Status Change', 'NEW', 'SHIPPED'
WHERE NOT EXISTS (
  SELECT 1 FROM orderupdates
  WHERE order_id = (SELECT order_id FROM orders o
                     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen')
                       AND o.user_id=(SELECT id FROM users WHERE username='sales1')
                       AND o.order_date='2025-07-17 00:00:00'
                       AND o.total_amount=300.00)
    AND status='SHIPPED'
);

INSERT INTO orderupdates (order_id, status, comment, update_type, old_value, new_value)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Dana Levi')
       AND o.user_id=(SELECT id FROM users WHERE username='admin')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=450.00),
  'DELIVERED', 'Order was successfully delivered', 'Status Change', 'SHIPPED', 'DELIVERED'
WHERE NOT EXISTS (
  SELECT 1 FROM orderupdates
  WHERE order_id = (SELECT order_id FROM orders o
                     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Dana Levi')
                       AND o.user_id=(SELECT id FROM users WHERE username='admin')
                       AND o.order_date='2025-07-17 00:00:00'
                       AND o.total_amount=450.00)
    AND status='DELIVERED'
);

INSERT INTO orderupdates (order_id, status, comment, update_type, old_value, new_value)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Amit Bar')
       AND o.user_id=(SELECT id FROM users WHERE username='warehouse1')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=180.00),
  'DELIVERED', 'Discount applied to order', 'Total Amount Update', '220.00', '180.00'
WHERE NOT EXISTS (
  SELECT 1 FROM orderupdates
  WHERE order_id = (SELECT order_id FROM orders o
                     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Amit Bar')
                       AND o.user_id=(SELECT id FROM users WHERE username='warehouse1')
                       AND o.order_date='2025-07-17 00:00:00'
                       AND o.total_amount=180.00)
    AND status='DELIVERED'
    AND update_type='Total Amount Update'
);

INSERT INTO orderupdates (order_id, status, comment, update_type, old_value, new_value)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen')
       AND o.user_id=(SELECT id FROM users WHERE username='support1')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=90.00),
  'NEW', 'Customer requested delay', 'Expected Delivery Date Change', '2025-07-17', '2025-07-20'
WHERE NOT EXISTS (
  SELECT 1 FROM orderupdates
  WHERE order_id = (SELECT order_id FROM orders o
                     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen')
                       AND o.user_id=(SELECT id FROM users WHERE username='support1')
                       AND o.order_date='2025-07-17 00:00:00'
                       AND o.total_amount=90.00)
    AND update_type='Expected Delivery Date Change'
);

INSERT INTO orderupdates (order_id, status, comment, update_type, old_value, new_value)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Noa Avraham')
       AND o.user_id=(SELECT id FROM users WHERE username='admin')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=0.00),
  'CANCELLED', 'Order cancelled by customer', 'Status Change', 'CONFIRMED', 'CANCELLED'
WHERE NOT EXISTS (
  SELECT 1 FROM orderupdates
  WHERE order_id = (SELECT order_id FROM orders o
                     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Noa Avraham')
                       AND o.user_id=(SELECT id FROM users WHERE username='admin')
                       AND o.order_date='2025-07-17 00:00:00'
                       AND o.total_amount=0.00)
    AND status='CANCELLED'
);

-- ===== SHIPMENTS =====
INSERT INTO shipments (order_id, tracking_number, shipping_provider, estimated_delivery_date, status)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen')
       AND o.user_id=(SELECT id FROM users WHERE username='sales1')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=300.00),
  'TRACK123', 'Israel Post', '2025-07-20', 'SHIPPED'
WHERE NOT EXISTS (SELECT 1 FROM shipments WHERE tracking_number='TRACK123');

INSERT INTO shipments (order_id, tracking_number, shipping_provider, estimated_delivery_date, status)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Dana Levi')
       AND o.user_id=(SELECT id FROM users WHERE username='admin')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=450.00),
  'FEDEX456', 'FedEx', '2025-07-22', 'IN TRANSIT'
WHERE NOT EXISTS (SELECT 1 FROM shipments WHERE tracking_number='FEDEX456');

INSERT INTO shipments (order_id, tracking_number, shipping_provider, estimated_delivery_date, status)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Amit Bar')
       AND o.user_id=(SELECT id FROM users WHERE username='warehouse1')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=180.00),
  'DHL789', 'DHL', '2025-07-25', 'DELIVERED'
WHERE NOT EXISTS (SELECT 1 FROM shipments WHERE tracking_number='DHL789');

INSERT INTO shipments (order_id, tracking_number, shipping_provider, estimated_delivery_date, status)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen')
       AND o.user_id=(SELECT id FROM users WHERE username='support1')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=90.00),
  'UPS555', 'UPS', '2025-07-21', 'PENDING'
WHERE NOT EXISTS (SELECT 1 FROM shipments WHERE tracking_number='UPS555');

INSERT INTO shipments (order_id, tracking_number, shipping_provider, estimated_delivery_date, status)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Noa Avraham')
       AND o.user_id=(SELECT id FROM users WHERE username='admin')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=0.00),
  'GLS222', 'GLS', '2025-07-23', 'RETURNED'
WHERE NOT EXISTS (SELECT 1 FROM shipments WHERE tracking_number='GLS222');

-- ===== DELIVERY STATUS =====
INSERT INTO deliverystatus (order_id, status, delay_reason)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen')
       AND o.user_id=(SELECT id FROM users WHERE username='sales1')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=300.00),
  'On Time', NULL
WHERE NOT EXISTS (
  SELECT 1 FROM deliverystatus
  WHERE order_id = (SELECT order_id FROM orders o
                     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen')
                       AND o.user_id=(SELECT id FROM users WHERE username='sales1')
                       AND o.order_date='2025-07-17 00:00:00'
                       AND o.total_amount=300.00)
);

INSERT INTO deliverystatus (order_id, status, delay_reason)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Dana Levi')
       AND o.user_id=(SELECT id FROM users WHERE username='admin')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=450.00),
  'Delayed', 'Customs issue'
WHERE NOT EXISTS (
  SELECT 1 FROM deliverystatus
  WHERE order_id = (SELECT order_id FROM orders o
                     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Dana Levi')
                       AND o.user_id=(SELECT id FROM users WHERE username='admin')
                       AND o.order_date='2025-07-17 00:00:00'
                       AND o.total_amount=450.00)
);

INSERT INTO deliverystatus (order_id, status, delay_reason)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Amit Bar')
       AND o.user_id=(SELECT id FROM users WHERE username='warehouse1')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=180.00),
  'Delivered', NULL
WHERE NOT EXISTS (
  SELECT 1 FROM deliverystatus
  WHERE order_id = (SELECT order_id FROM orders o
                     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Amit Bar')
                       AND o.user_id=(SELECT id FROM users WHERE username='warehouse1')
                       AND o.order_date='2025-07-17 00:00:00'
                       AND o.total_amount=180.00)
);

INSERT INTO deliverystatus (order_id, status, delay_reason)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen')
       AND o.user_id=(SELECT id FROM users WHERE username='support1')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=90.00),
  'Delayed', 'Logistics problem'
WHERE NOT EXISTS (
  SELECT 1 FROM deliverystatus
  WHERE order_id = (SELECT order_id FROM orders o
                     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Yossi Cohen')
                       AND o.user_id=(SELECT id FROM users WHERE username='support1')
                       AND o.order_date='2025-07-17 00:00:00'
                       AND o.total_amount=90.00)
);

INSERT INTO deliverystatus (order_id, status, delay_reason)
SELECT
  (SELECT order_id FROM orders o
     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Noa Avraham')
       AND o.user_id=(SELECT id FROM users WHERE username='admin')
       AND o.order_date='2025-07-17 00:00:00'
       AND o.total_amount=0.00),
  'In Transit', NULL
WHERE NOT EXISTS (
  SELECT 1 FROM deliverystatus
  WHERE order_id = (SELECT order_id FROM orders o
                     WHERE o.customer_id=(SELECT customer_id FROM customers WHERE contact_name='Noa Avraham')
                       AND o.user_id=(SELECT id FROM users WHERE username='admin')
                       AND o.order_date='2025-07-17 00:00:00'
                       AND o.total_amount=0.00)
);

-- ===== INVENTORY =====
INSERT INTO inventory (product_id, quantity) VALUES
  ((SELECT id FROM products WHERE name='אסלה תלויה'),       120),
  ((SELECT id FROM products WHERE name='ניאגרה סמויה'),     65),
  ((SELECT id FROM products WHERE name='ברז כיור נמוך'),    30),
  ((SELECT id FROM products WHERE name='מראה עם תאורה'),    95),
  ((SELECT id FROM products WHERE name='מתלה מגבות קיר'),   50)
ON CONFLICT (product_id) DO NOTHING;

-- ===== INVENTORY HISTORY =====
INSERT INTO inventoryhistory (product_id, change, note) VALUES
  ((SELECT id FROM products WHERE name='ברז מטבח נשלף'), 100, 'Initial stock'),
  ((SELECT id FROM products WHERE name='ראש טוש עגול'),   50, 'Initial stock'),
  ((SELECT id FROM products WHERE name='כיור מונח עגול'), 75, 'Initial stock'),
  ((SELECT id FROM products WHERE name='ברז אמבטיה קיר'), 30, 'Initial stock'),
  ((SELECT id FROM products WHERE name='סיפון נירוסטה'),  60, 'Initial stock')
ON CONFLICT DO NOTHING;

-- ===== SUPPLIER INVENTORY =====
-- סדר העמודות: (supplier_id, product_id, quantity, unit_price)
INSERT INTO supplierinventory (supplier_id, product_id, quantity, unit_price)
SELECT (SELECT id FROM suppliers WHERE company_name='Sanifix Ltd.'),
       (SELECT id FROM products  WHERE name='ברז מטבח נשלף'),
       120, 345.00
WHERE NOT EXISTS (
  SELECT 1 FROM supplierinventory si
  WHERE si.supplier_id=(SELECT id FROM suppliers WHERE company_name='Sanifix Ltd.')
    AND si.product_id =(SELECT id FROM products  WHERE name='ברז מטבח נשלף')
);

INSERT INTO supplierinventory (supplier_id, product_id, quantity, unit_price)
SELECT (SELECT id FROM suppliers WHERE company_name='AquaPro Systems'),
       (SELECT id FROM products  WHERE name='ראש טוש עגול'),
       80, 190.00
WHERE NOT EXISTS (
  SELECT 1 FROM supplierinventory si
  WHERE si.supplier_id=(SELECT id FROM suppliers WHERE company_name='AquaPro Systems')
    AND si.product_id =(SELECT id FROM products  WHERE name='ראש טוש עגול')
);

INSERT INTO supplierinventory (supplier_id, product_id, quantity, unit_price)
SELECT (SELECT id FROM suppliers WHERE company_name='Nir Faucets'),
       (SELECT id FROM products  WHERE name='כיור מונח עגול'),
       50, 420.00
WHERE NOT EXISTS (
  SELECT 1 FROM supplierinventory si
  WHERE si.supplier_id=(SELECT id FROM suppliers WHERE company_name='Nir Faucets')
    AND si.product_id =(SELECT id FROM products  WHERE name='כיור מונח עגול')
);

INSERT INTO supplierinventory (supplier_id, product_id, quantity, unit_price)
SELECT (SELECT id FROM suppliers WHERE company_name='PlumbLine'),
       (SELECT id FROM products  WHERE name='ברז אמבטיה קיר'),
       35, 570.00
WHERE NOT EXISTS (
  SELECT 1 FROM supplierinventory si
  WHERE si.supplier_id=(SELECT id FROM suppliers WHERE company_name='PlumbLine')
    AND si.product_id =(SELECT id FROM products  WHERE name='ברז אמבטיה קיר')
);

INSERT INTO supplierinventory (supplier_id, product_id, quantity, unit_price)
SELECT (SELECT id FROM suppliers WHERE company_name='HydroFlow'),
       (SELECT id FROM products  WHERE name='סיפון נירוסטה'),
       200, 70.00
WHERE NOT EXISTS (
  SELECT 1 FROM supplierinventory si
  WHERE si.supplier_id=(SELECT id FROM suppliers WHERE company_name='HydroFlow')
    AND si.product_id =(SELECT id FROM products  WHERE name='סיפון נירוסטה')
);

INSERT INTO supplierinventory (supplier_id, product_id, quantity, unit_price)
SELECT (SELECT id FROM suppliers WHERE company_name='TapTech'),
       (SELECT id FROM products  WHERE name='אסלה תלויה'),
       25, 1100.00
WHERE NOT EXISTS (
  SELECT 1 FROM supplierinventory si
  WHERE si.supplier_id=(SELECT id FROM suppliers WHERE company_name='TapTech')
    AND si.product_id =(SELECT id FROM products  WHERE name='אסלה תלויה')
);

INSERT INTO supplierinventory (supplier_id, product_id, quantity, unit_price)
SELECT (SELECT id FROM suppliers WHERE company_name='FlowFix'),
       (SELECT id FROM products  WHERE name='ניאגרה סמויה'),
       40, 940.00
WHERE NOT EXISTS (
  SELECT 1 FROM supplierinventory si
  WHERE si.supplier_id=(SELECT id FROM suppliers WHERE company_name='FlowFix')
    AND si.product_id =(SELECT id FROM products  WHERE name='ניאגרה סמויה')
);

INSERT INTO supplierinventory (supplier_id, product_id, quantity, unit_price)
SELECT (SELECT id FROM suppliers WHERE company_name='DripMaster'),
       (SELECT id FROM products  WHERE name='ברז כיור נמוך'),
       60, 295.00
WHERE NOT EXISTS (
  SELECT 1 FROM supplierinventory si
  WHERE si.supplier_id=(SELECT id FROM suppliers WHERE company_name='DripMaster')
    AND si.product_id =(SELECT id FROM products  WHERE name='ברז כיור נמוך')
);

INSERT INTO supplierinventory (supplier_id, product_id, quantity, unit_price)
SELECT (SELECT id FROM suppliers WHERE company_name='AquaPro Elite'),
       (SELECT id FROM products  WHERE name='מראה עם תאורה'),
       15, 620.00
WHERE NOT EXISTS (
  SELECT 1 FROM supplierinventory si
  WHERE si.supplier_id=(SELECT id FROM suppliers WHERE company_name='AquaPro Elite')
    AND si.product_id =(SELECT id FROM products  WHERE name='מראה עם תאורה')
);

INSERT INTO supplierinventory (supplier_id, product_id, quantity, unit_price)
SELECT (SELECT id FROM suppliers WHERE company_name='SanitaryPro'),
       (SELECT id FROM products  WHERE name='מתלה מגבות קיר'),
       100, 105.00
WHERE NOT EXISTS (
  SELECT 1 FROM supplierinventory si
  WHERE si.supplier_id=(SELECT id FROM suppliers WHERE company_name='SanitaryPro')
    AND si.product_id =(SELECT id FROM products  WHERE name='מתלה מגבות קיר')
);
