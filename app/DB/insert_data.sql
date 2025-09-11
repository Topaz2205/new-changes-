

-- === Roles ===

INSERT OR IGNORE INTO Roles (id, name) VALUES
(1, 'Admin'), (2, 'SalesManager'), (3, 'WarehouseManager'),
(4, 'CustomerService'), (5, 'User');

-- === Permissions ===

INSERT OR IGNORE INTO Permissions (name) VALUES
('view_inventory'), ('manage_inventory'),
('view_orders'), ('manage_orders'),
('view_users'), ('manage_users');



-- === Users ===

INSERT OR IGNORE INTO Users (username, email, password, role_id) VALUES
('admin', 'admin@example.com', 'adminpass', 1),
('sales1', 'sales1@example.com', 'salespass', 2),
('warehouse1', 'warehouse1@example.com', 'warehousepass', 3),
('support1', 'support1@example.com', 'supportpass', 4),
('user1', 'user1@example.com', 'userpass', 5);

-- === RolePermissions ===



-- Admin: all core permissions
INSERT OR IGNORE INTO RolePermissions (role_id, permission_id)
SELECT r.id, p.id
FROM Roles r
JOIN Permissions p ON p.name IN (
  'manage_users','view_users',
  'view_orders','manage_orders',
  'view_inventory','manage_inventory'
)
WHERE r.name = 'Admin';

-- SalesManager: orders -> view + manage
INSERT OR IGNORE INTO RolePermissions (role_id, permission_id)
SELECT r.id, p.id
FROM Roles r
JOIN Permissions p ON p.name IN ('view_orders','manage_orders')
WHERE r.name = 'SalesManager';

-- WarehouseManager: inventory -> view + manage  (the new addition for requirement #2)
INSERT OR IGNORE INTO RolePermissions (role_id, permission_id)
SELECT r.id, p.id
FROM Roles r
JOIN Permissions p ON p.name IN ('view_inventory','manage_inventory')
WHERE r.name = 'WarehouseManager';

-- CustomerService: orders -> view + manage  (the new addition for requirement #2)
INSERT OR IGNORE INTO RolePermissions (role_id, permission_id)
SELECT r.id, p.id
FROM Roles r
JOIN Permissions p ON p.name IN ('view_orders','manage_orders')
WHERE r.name = 'CustomerService';

-- User (end-user/basic): minimal two processes (views)
INSERT OR IGNORE INTO RolePermissions (role_id, permission_id)
SELECT r.id, p.id
FROM Roles r
JOIN Permissions p ON p.name IN ('view_orders','view_inventory')
WHERE r.name = 'User';



-- === Suppliers ===

INSERT OR IGNORE INTO Suppliers (company_name, contact_name, contact_email, address, city, country, phone) VALUES
('Sanifix Ltd.', 'Ronen Levi', 'ronen@sanifix.com', 'Hamerkava 5', 'Petah Tikva', 'Israel', '03-6100000'),
('AquaPro Systems', 'Dana Cohen', 'dana@aquapro.co.il', 'Shlomo St 12', 'Rishon Lezion', 'Israel', '03-9201111'),
('Nir Faucets', 'Yossi Nir', 'yossi@nirfaucets.com', 'HaHarash 3', 'Haifa', 'Israel', '04-8555555'),
('PlumbLine', 'Maya Bar', 'maya@plumbline.co.il', 'Yitzhak Sade 22', 'Tel Aviv', 'Israel', '03-9456789'),
('HydroFlow', 'Lior Maman', 'lior@hydroflow.co.il', 'Herzl 10', 'Netanya', 'Israel', '09-4567890'),
('TapTech', 'Avi Mizrahi', 'avi@taptech.com', 'Hapardes 8', 'Beer Sheva', 'Israel', '08-6543210'),
('FlowFix', 'Tal Levi', 'tal@flowfix.com', 'Hamagen 20', 'Ashdod', 'Israel', '08-8888888'),
('DripMaster', 'Noa Azulay', 'noa@dripmaster.co.il', 'Derech HaAtzmaut 15', 'Bat Yam', 'Israel', '03-3334444'),
('AquaPro Elite', 'Gil Ben Haim', 'gil@aquaproelite.com', 'Ben Gurion 19', 'Kfar Saba', 'Israel', '09-7777777'),
('SanitaryPro', 'Shira Gold', 'shira@sanitarypro.co.il', 'Jabotinsky 88', 'Ramat Gan', 'Israel', '03-4449999');

-- === Categories ===

INSERT OR IGNORE INTO Categories (id, name, description) VALUES
(1, 'ברזים', 'ברזים לאמבטיה, כיור ומטבח'),
(2, 'כיורים', 'כיורי מטבח ואמבטיה מכל הסוגים'),
(3, 'אסלות', 'אסלות תלייה, אסלות רגילות ומערכות הדחה'),
(4, 'אמבטיות', 'אמבטיות פרי סטנדינג, פינתיות ועוד'),
(5, 'מקלחונים', 'מקלחונים עם דלתות הזזה או פתיחה רגילה'),
(6, 'ארונות אמבטיה', 'פתרונות אחסון לחדרי רחצה'),
(7, 'ברזי מטבח', 'ברזים עם מקלחת נשלפת או זרם כפול'),
(8, 'אביזרי תלייה', 'ווים, מתקני מגבות, מחזיקי נייר טואלט'),
(9, 'ניאגרות', 'מערכות הדחה סמויות וגלויות'),
(10, 'כלים לאינסטלציה', 'צנרת, מחברים ואביזרי התקנה');

-- === Shippers ===

INSERT OR IGNORE INTO Shippers (company_name, phone) VALUES
('FedEx', '1-800-463-3339'),
('UPS', '1-800-742-5877'),
('DHL', '1-800-225-5345'),
('Israel Post', '1-700-500-171'),
('ZigZag Express', '03-900-1234');

-- === ProductColors ===
INSERT OR IGNORE INTO ProductColors (id, color_name, hex_code) VALUES
(1, 'כרום', '#C0C0C0'),
(2, 'כסוף', '#C0C0C0'),
(3, 'לבן', '#FFFFFF'),
(4, 'שחור מט', '#1C1C1C'),
(5, 'נירוסטה', '#B0B0B0'),
(6, 'ניקל מוברש', '#D3D3D3'),
(7, 'נירוסטה מבריקה', '#A9A9A9');

-- === Products ===
INSERT OR IGNORE INTO Products (id, name, supplier_id, category_id, quantity_per_unit, color_id, price, discontinued) VALUES
(1, 'ברז מטבח נשלף', 1, 1, '1 יחידה', 1, 349.90, 0),  -- כרום
(2, 'ראש טוש עגול', 2, 5, '1 יחידה', 2, 199.00, 0),   -- כסוף
(3, 'כיור מונח עגול', 3, 2, '1 יחידה', 3, 450.00, 0),  -- לבן
(4, 'ברז אמבטיה קיר', 1, 1, '1 יחידה', 4, 599.00, 0), -- שחור מט
(5, 'סיפון נירוסטה', 7, 10, '1 יחידה', 5, 75.00, 0),  -- נירוסטה
(6, 'אסלה תלויה', 5, 3, '1 יחידה', 3, 1200.00, 0),     -- לבן
(7, 'ניאגרה סמויה', 4, 9, '1 יחידה', 3, 990.00, 0),    -- לבן
(8, 'ברז כיור נמוך', 3, 1, '1 יחידה', 6, 310.00, 0),   -- ניקל מוברש
(9, 'מראה עם תאורה', 8, 6, '1 יחידה', 2, 680.00, 0),   -- כסוף
(10, 'מתלה מגבות קיר', 9, 8, '1 יחידה', 7, 115.00, 0); -- נירוסטה מבריקה

-- === Customers ===

INSERT OR IGNORE INTO Customers (contact_name, contact_title, address, customer_type, customer_tag, city, postal_code, country, phone, email) VALUES
('Yossi Cohen', 'Mr.', 'Herzl 10', 'Private', 'VIP', 'Tel Aviv', '61000', 'Israel', '050-1234567', 'yossi@example.com'),
('Dana Levi', 'Ms.', 'HaAtzmaut 5', 'Business', 'Priority', 'Haifa', '32000', 'Israel', '054-9876543', 'dana@example.com'),
('Amit Bar', 'Mr.', 'Weizmann 22', 'Private', 'New', 'Jerusalem', '91000', 'Israel', '052-4567890', 'amitb@example.com'),
('Roni Gilad', 'Mrs.', 'Ben Gurion 8', 'Business', 'Returning', 'Ramat Gan', '52000', 'Israel', '053-3214567', 'ronig@example.com'),
('Noa Avraham', 'Ms.', 'Begin 3', 'Private', 'Regular', 'Ashdod', '77000', 'Israel', '054-8765432', 'noaa@example.com');


-- === Employees ===

INSERT OR IGNORE INTO Employees (user_id, first_name, last_name, position, birth_date, hire_date, address, city, postal_code, country, phone, email, manager_id)
VALUES 
(1, 'David', 'Levi', 'CEO', '1980-01-01', '2010-01-01', 'Hasharon 1', 'Tel Aviv', '61000', 'Israel', '0501234567', 'david@sanitary.com', NULL),
(2, 'Rina', 'Cohen', 'Sales Manager', '1985-02-02', '2015-03-01', 'Herzl 2', 'Haifa', '32000', 'Israel', '0502345678', 'rina@sanitary.com', 1),
(3, 'Oren', 'Mizrahi', 'Warehouse Manager', '1983-03-03', '2014-04-01', 'Begin 3', 'Beer Sheva', '84000', 'Israel', '0503456789', 'oren@sanitary.com', 1),
(4, 'Maya', 'Bar', 'Support Manager', '1990-04-04', '2018-05-01', 'Ben Yehuda 4', 'Jerusalem', '91000', 'Israel', '0504567890', 'maya@sanitary.com', 1),
(5, 'Yoni', 'Katz', 'Sales Rep', '1992-05-05', '2020-06-01', 'HaPalmach 5', 'Ashdod', '77000', 'Israel', '0505678901', 'yoni@sanitary.com', 2);

-- === Orders (כולל order_date) ===
INSERT OR IGNORE INTO Orders (
    order_id, customer_id, employee_id, user_id, status,
    ship_via, freight, total_amount,
    expected_delivery, actual_delivery, shipped_date, order_date
) VALUES
(1, 1, 1, 2, 'Pending', 'FedEx', 25.50, 300.00, '2025-07-25 00:00:00', NULL, NULL, '2025-07-17 00:00:00'),
(2, 2, 2, 1, 'Shipped', 'DHL', 15.00, 450.00, '2025-07-20 00:00:00', NULL, '2025-07-18 00:00:00', '2025-07-17 00:00:00'),
(3, 3, 3, 3, 'Delivered', 'UPS', 12.00, 180.00, '2025-07-10 00:00:00', '2025-07-11 00:00:00', '2025-07-10 00:00:00', '2025-07-17 00:00:00'),
(4, 1, 4, 4, 'Pending', 'Self Pickup', 0.00, 90.00, '2025-07-28 00:00:00', NULL, NULL, '2025-07-17 00:00:00'),
(5, 5, 2, 1, 'Cancelled', 'GLS', 20.00, 0.00, '2025-07-30 00:00:00', NULL, NULL, '2025-07-17 00:00:00');

-- === OrderItems ===

INSERT OR IGNORE INTO OrderItems (order_id, product_id, quantity, price_at_order) VALUES
(1, 2, 1, 499.99),
(2, 5, 1, 149.99),
(3, 4, 1, 89.99),
(4, 3, 1, 199.99);

-- === OrderUpdates ===

INSERT OR IGNORE INTO OrderUpdates (order_id, status,comment, update_type, old_value, new_value) VALUES
(1, 'Shipped', 'Changed status', 'Status Change', 'Pending', 'Shipped'),
(2, 'Delivered', 'Order was successfully delivered', 'Status Change', 'Shipped', 'Delivered'),
(3, 'Delivered', 'Discount applied to order', 'Total Amount Update', '220.00', '180.00'),
(4, 'Pending', 'Customer requested delay', 'Expected Delivery Date Change', '2025-07-17', '2025-07-20'),
(5, 'Cancelled', 'Order cancelled by customer', 'Status Change', 'Confirmed', 'Cancelled');

-- === Shipments ===

INSERT OR IGNORE INTO Shipments (order_id, tracking_number, shipping_provider, estimated_delivery_date, status) VALUES
(1, 'TRACK123', 'Israel Post', '2025-07-20', 'Shipped'),
(2, 'FEDEX456', 'FedEx', '2025-07-22', 'In Transit'),
(3, 'DHL789', 'DHL', '2025-07-25', 'Delivered'),
(4, 'UPS555', 'UPS', '2025-07-21', 'Pending'),
(5, 'GLS222', 'GLS', '2025-07-23', 'Returned');

-- === DeliveryStatus ===

INSERT OR IGNORE INTO DeliveryStatus (order_id, status, delay_reason) VALUES
(1, 'On Time', NULL),
(2, 'Delayed', 'Customs issue'),
(3, 'Delivered', NULL),
(4, 'Delayed', 'Logistics problem'),
(5, 'In Transit', NULL);

-- === Inventory ===

INSERT OR IGNORE INTO Inventory (product_id, quantity) VALUES
(6, 120),
(7, 65),
(8, 30),
(9, 95),
(10, 50);

-- === InventoryHistory ===

INSERT OR IGNORE INTO InventoryHistory (product_id, change, note) VALUES
(1, +100, 'Initial stock'),
(2, +50, 'Initial stock'),
(3, +75, 'Initial stock'),
(4, +30, 'Initial stock'),
(5, +60, 'Initial stock');



-- === SupplierInventory ===

INSERT OR IGNORE INTO SupplierInventory (product_id, supplier_id, quantity, unit_price) VALUES
(1, 1, 120, 345.00),
(2, 2, 80, 190.00),
(3, 3, 50, 420.00),
(4, 4, 35, 570.00),
(5, 5, 200, 70.00),
(6, 6, 25, 1100.00),
(7, 7, 40, 940.00),
(8, 8, 60, 295.00),
(9, 9, 15, 620.00),
(10, 10, 100, 105.00);
