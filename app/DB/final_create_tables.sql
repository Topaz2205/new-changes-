PRAGMA foreign_keys = ON;
-- === Roles ===
CREATE TABLE IF NOT EXISTS Roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
-- === Permissions ===
CREATE TABLE IF NOT EXISTS Permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
-- === Users ===
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES Roles(id)
);
-- === RolePermissions ===
CREATE TABLE IF NOT EXISTS RolePermissions (
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES Roles(id),
    FOREIGN KEY (permission_id) REFERENCES Permissions(id)
);

-- === Suppliers ===
CREATE TABLE IF NOT EXISTS Suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL UNIQUE,
    contact_name TEXT,
    contact_email TEXT,
    address TEXT,
    city TEXT,
    country TEXT,
    phone TEXT
);

-- === Categories ===
CREATE TABLE IF NOT EXISTS Categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- === Shippers ===
CREATE TABLE IF NOT EXISTS Shippers (
    shipper_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    phone TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- === ProductColors ===
CREATE TABLE IF NOT EXISTS ProductColors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    color_name TEXT NOT NULL,
    hex_code TEXT
);


-- === Products ===
CREATE TABLE IF NOT EXISTS Products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    image_url TEXT,
    units_in_stock INTEGER DEFAULT 0,
    quantity_per_unit TEXT,
    color_id INTEGER,
    discontinued BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES Categories(id),
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(id),
    FOREIGN KEY (color_id) REFERENCES ProductColors(id)
);
-- === Customers ===
CREATE TABLE IF NOT EXISTS Customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_name TEXT NOT NULL,
    contact_title TEXT,
    address TEXT,
    customer_type TEXT,
    customer_tag TEXT,
    city TEXT,
    postal_code TEXT,
    country TEXT,
    phone TEXT,
    email TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
-- === Employees ===
CREATE TABLE IF NOT EXISTS Employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    first_name TEXT,
    last_name TEXT,
    position TEXT,
    birth_date TEXT,
    hire_date TEXT,
    address TEXT,
    city TEXT,
    postal_code TEXT,
    country TEXT,
    phone TEXT,
    email TEXT,
    manager_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (manager_id) REFERENCES Employees(id)
);
-- === Orders ===
CREATE TABLE IF NOT EXISTS Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    employee_id INTEGER,
    status TEXT NOT NULL,
    total_amount REAL,
    freight REAL,
    ship_via TEXT,
    expected_delivery DATETIME,
    actual_delivery DATETIME,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    shipped_date DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
    FOREIGN KEY (employee_id) REFERENCES Employees(id)
    );
-- === OrderItems ===
CREATE TABLE IF NOT EXISTS OrderItems (
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    price_at_order REAL NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Products(id)
);
-- === OrderUpdates ===
CREATE TABLE IF NOT EXISTS OrderUpdates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    update_ts DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT,
    comment TEXT,
    update_type TEXT,     
    old_value TEXT,       
    new_value TEXT,       
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);
-- === Shipments ===
CREATE TABLE IF NOT EXISTS Shipments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    tracking_number TEXT,
    shipping_provider TEXT,
    shipped_date DATETIME,
    estimated_delivery_date DATETIME,
    delivery_date DATETIME,
    status TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);
-- === DeliveryStatus ===
CREATE TABLE IF NOT EXISTS DeliveryStatus (
    status_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    delay_reason TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);
-- === Inventory ===
CREATE TABLE IF NOT EXISTS Inventory (
    product_id INTEGER PRIMARY KEY,
    quantity INTEGER NOT NULL DEFAULT 0,
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES Products(id)
);
-- === InventoryHistory ===
CREATE TABLE IF NOT EXISTS InventoryHistory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    change INTEGER NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    note TEXT,
    FOREIGN KEY (product_id) REFERENCES Products(id)
);

-- === SupplierInventory ===
CREATE TABLE IF NOT EXISTS SupplierInventory (
    supplier_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    unit_price REAL DEFAULT 0.0,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (supplier_id, product_id),
    FOREIGN KEY (supplier_id) REFERENCES Suppliers(id),
    FOREIGN KEY (product_id) REFERENCES Products(id)
);
