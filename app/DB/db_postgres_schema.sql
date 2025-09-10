-- db_postgres_schema.sql (מינימום שינויים מ-SQLite)
-- סוגים: SERIAL במקום AUTOINCREMENT, TIMESTAMPTZ במקום DATETIME, BOOLEAN אמיתי

CREATE TABLE IF NOT EXISTS Roles (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Permissions (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS RolePermissions (
  role_id INTEGER NOT NULL,
  permission_id INTEGER NOT NULL,
  PRIMARY KEY (role_id, permission_id),
  FOREIGN KEY (role_id) REFERENCES Roles(id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (permission_id) REFERENCES Permissions(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Users (
  id SERIAL PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  role_id INTEGER NOT NULL,
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (role_id) REFERENCES Roles(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Customers (
  customer_id SERIAL PRIMARY KEY,
  contact_name TEXT,
  address TEXT,
  city TEXT,
  postal_code TEXT,
  country TEXT,
  phone TEXT,
  email TEXT
);

CREATE TABLE IF NOT EXISTS Employees (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL UNIQUE,
  first_name TEXT,
  last_name TEXT,
  position TEXT,
  birth_date DATE,
  hire_date DATE,
  address TEXT,
  city TEXT,
  postal_code TEXT,
  country TEXT,
  phone TEXT,
  email TEXT,
  manager_id INTEGER,
  FOREIGN KEY (user_id)   REFERENCES Users(id)      ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (manager_id) REFERENCES Employees(id) ON DELETE SET NULL  ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Categories (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Suppliers (
  id SERIAL PRIMARY KEY,
  company_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ProductColors (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Products (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  category_id INTEGER NOT NULL,
  supplier_id INTEGER NOT NULL,
  description TEXT,
  price NUMERIC(12,2) NOT NULL,
  image_url TEXT,
  units_in_stock INTEGER DEFAULT 0,
  quantity_per_unit TEXT,
  color_id INTEGER,
  discontinued BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (category_id) REFERENCES Categories(id)    ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (supplier_id) REFERENCES Suppliers(id)     ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (color_id)    REFERENCES ProductColors(id) ON DELETE SET NULL  ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Orders (
  order_id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  customer_id INTEGER NOT NULL,
  employee_id INTEGER,
  status TEXT NOT NULL CHECK (status IN ('NEW','PAID','SHIPPED','DELIVERED','CANCELLED')),
  total_amount NUMERIC(12,2),
  freight NUMERIC(12,2),
  ship_via TEXT,
  expected_delivery TIMESTAMPTZ,
  actual_delivery TIMESTAMPTZ,
  order_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  shipped_date TIMESTAMPTZ,
  updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id)     REFERENCES Users(id)         ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (employee_id) REFERENCES Employees(id)     ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS OrderItems (
  order_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL DEFAULT 1,
  price_at_order NUMERIC(12,2) NOT NULL,
  PRIMARY KEY (order_id, product_id),
  FOREIGN KEY (order_id)  REFERENCES Orders(order_id)  ON DELETE CASCADE  ON UPDATE CASCADE,
  FOREIGN KEY (product_id) REFERENCES Products(id)     ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Inventory (
  product_id INTEGER PRIMARY KEY,
  quantity INTEGER NOT NULL DEFAULT 0,
  last_updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES Products(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS InventoryHistory (
  id SERIAL PRIMARY KEY,
  product_id INTEGER NOT NULL,
  change INTEGER NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  note TEXT,
  FOREIGN KEY (product_id) REFERENCES Products(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Shipments (
  id SERIAL PRIMARY KEY,
  order_id INTEGER NOT NULL,
  tracking_number TEXT,
  shipping_provider TEXT,
  shipped_date TIMESTAMPTZ,
  estimated_delivery_date TIMESTAMPTZ,
  delivery_date TIMESTAMPTZ,
  status TEXT NOT NULL,
  FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS DeliveryStatus (
  status_id SERIAL PRIMARY KEY,
  order_id INTEGER NOT NULL,
  status TEXT NOT NULL,
  delay_reason TEXT,
  updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS SupplierInventory (
  supplier_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  quantity INTEGER NOT NULL DEFAULT 0,
  unit_price NUMERIC(12,2) DEFAULT 0.0,
  last_updated TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (supplier_id, product_id),
  FOREIGN KEY (supplier_id) REFERENCES Suppliers(id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (product_id)  REFERENCES Products(id)  ON DELETE CASCADE ON UPDATE CASCADE
);

-- אינדקסים (תואם למה שעשית ב-SQLite)
CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON Orders(customer_id, order_date DESC);
CREATE INDEX IF NOT EXISTS idx_orders_employee      ON Orders(employee_id);
CREATE INDEX IF NOT EXISTS idx_orders_user          ON Orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status        ON Orders(status);

CREATE INDEX IF NOT EXISTS idx_orderitems_order     ON OrderItems(order_id);
CREATE INDEX IF NOT EXISTS idx_orderitems_product   ON OrderItems(product_id);

CREATE INDEX IF NOT EXISTS idx_products_category    ON Products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_supplier    ON Products(supplier_id);
CREATE INDEX IF NOT EXISTS idx_products_color       ON Products(color_id);
CREATE INDEX IF NOT EXISTS idx_products_name        ON Products(name);

CREATE INDEX IF NOT EXISTS idx_inventoryhist_prod_time ON InventoryHistory(product_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_shipments_order      ON Shipments(order_id);
CREATE INDEX IF NOT EXISTS idx_deliverystatus_order ON DeliveryStatus(order_id);

CREATE INDEX IF NOT EXISTS idx_customers_phone      ON Customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_email      ON Customers(email);
CREATE INDEX IF NOT EXISTS idx_users_role           ON Users(role_id);
CREATE INDEX IF NOT EXISTS idx_rolepermissions_role ON RolePermissions(role_id);

CREATE INDEX IF NOT EXISTS idx_supplierinventory_supplier ON SupplierInventory(supplier_id);
CREATE INDEX IF NOT EXISTS idx_supplierinventory_product  ON SupplierInventory(product_id);
