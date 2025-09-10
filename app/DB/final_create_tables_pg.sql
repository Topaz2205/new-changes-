
-- Roles
CREATE TABLE IF NOT EXISTS roles (
    id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE
);

-- Permissions
CREATE TABLE IF NOT EXISTS permissions (
    id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE
);

-- Users
CREATE TABLE IF NOT EXISTS users (
    id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username   TEXT NOT NULL UNIQUE,
    email      TEXT NOT NULL UNIQUE,
    password   TEXT NOT NULL,
    role_id    INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_users_role
      FOREIGN KEY (role_id) REFERENCES roles(id)
      ON DELETE RESTRICT ON UPDATE CASCADE
);

-- RolePermissions
CREATE TABLE IF NOT EXISTS rolepermissions (
    role_id       INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    CONSTRAINT fk_rp_role
      FOREIGN KEY (role_id) REFERENCES roles(id)
      ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_rp_perm
      FOREIGN KEY (permission_id) REFERENCES permissions(id)
      ON DELETE CASCADE ON UPDATE CASCADE
);

-- Suppliers
CREATE TABLE IF NOT EXISTS suppliers (
    id            INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    company_name  TEXT NOT NULL UNIQUE,
    contact_name  TEXT,
    contact_email TEXT,
    address       TEXT,
    city          TEXT,
    country       TEXT,
    phone         TEXT
);

-- Categories
CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Shippers
CREATE TABLE IF NOT EXISTS shippers (
    shipper_id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    company_name TEXT NOT NULL,
    phone        TEXT,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ProductColors
CREATE TABLE IF NOT EXISTS productcolors (
    id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    color_name TEXT NOT NULL,
    hex_code   TEXT
);

-- Products
CREATE TABLE IF NOT EXISTS products (
    id                INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name              TEXT NOT NULL,
    category_id       INTEGER NOT NULL,
    supplier_id       INTEGER NOT NULL,
    description       TEXT,
    price             NUMERIC(12,2) NOT NULL,
    image_url         TEXT,
    units_in_stock    INTEGER DEFAULT 0,
    quantity_per_unit TEXT,
    color_id          INTEGER,
    discontinued      BOOLEAN DEFAULT FALSE,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_prod_cat  FOREIGN KEY (category_id) REFERENCES categories(id)    ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_prod_sup  FOREIGN KEY (supplier_id) REFERENCES suppliers(id)     ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_prod_col  FOREIGN KEY (color_id)    REFERENCES productcolors(id) ON DELETE SET NULL  ON UPDATE CASCADE
);

-- Customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    contact_name  TEXT NOT NULL,
    contact_title TEXT,
    address       TEXT,
    customer_type TEXT,
    customer_tag  TEXT,
    city          TEXT,
    postal_code   TEXT,
    country       TEXT,
    phone         TEXT,
    email         TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Employees
CREATE TABLE IF NOT EXISTS employees (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     INTEGER NOT NULL UNIQUE,
    first_name  TEXT,
    last_name   TEXT,
    position    TEXT,
    birth_date  DATE,
    hire_date   DATE,
    address     TEXT,
    city        TEXT,
    postal_code TEXT,
    country     TEXT,
    phone       TEXT,
    email       TEXT,
    manager_id  INTEGER,
    CONSTRAINT fk_emp_user FOREIGN KEY (user_id)    REFERENCES users(id)      ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_emp_mgr  FOREIGN KEY (manager_id) REFERENCES employees(id)  ON DELETE SET NULL  ON UPDATE CASCADE
);

-- Orders
CREATE TABLE IF NOT EXISTS orders (
    order_id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id           INTEGER NOT NULL,
    customer_id       INTEGER NOT NULL,
    employee_id       INTEGER,
    status            TEXT NOT NULL CHECK (status IN ('NEW','PAID','SHIPPED','DELIVERED','CANCELLED')),
    total_amount      NUMERIC(12,2),
    freight           NUMERIC(12,2),
    ship_via          TEXT,
    expected_delivery TIMESTAMPTZ,
    actual_delivery   TIMESTAMPTZ,
    order_date        TIMESTAMPTZ DEFAULT NOW(),
    shipped_date      TIMESTAMPTZ,
    updated_at        TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_ord_user FOREIGN KEY (user_id)     REFERENCES users(id),
    CONSTRAINT fk_ord_cust FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_ord_emp  FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- Index for orders.status
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- OrderItems
CREATE TABLE IF NOT EXISTS orderitems (
    order_id       INTEGER NOT NULL,
    product_id     INTEGER NOT NULL,
    quantity       INTEGER NOT NULL DEFAULT 1,
    price_at_order NUMERIC(12,2) NOT NULL,
    PRIMARY KEY (order_id, product_id),
    CONSTRAINT fk_oi_order FOREIGN KEY (order_id)  REFERENCES orders(order_id)  ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_oi_prod  FOREIGN KEY (product_id) REFERENCES products(id)     ON DELETE RESTRICT ON UPDATE CASCADE
);

-- OrderUpdates
CREATE TABLE IF NOT EXISTS orderupdates (
    id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id   INTEGER NOT NULL,
    update_ts  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status     TEXT,
    comment    TEXT,
    update_type TEXT,
    old_value  TEXT,
    new_value  TEXT,
    CONSTRAINT fk_oupd_order FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- Shipments
CREATE TABLE IF NOT EXISTS shipments (
    id                      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id                INTEGER NOT NULL,
    tracking_number         TEXT,
    shipping_provider       TEXT,
    shipped_date            TIMESTAMPTZ,
    estimated_delivery_date TIMESTAMPTZ,
    delivery_date           TIMESTAMPTZ,
    status                  TEXT NOT NULL,
    CONSTRAINT fk_ship_order FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- DeliveryStatus
CREATE TABLE IF NOT EXISTS deliverystatus (
    status_id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id    INTEGER NOT NULL,
    status      TEXT NOT NULL,
    delay_reason TEXT,
    updated_at  TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_dstat_order FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Inventory
CREATE TABLE IF NOT EXISTS inventory (
    product_id   INTEGER PRIMARY KEY,
    quantity     INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_inv_prod FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- InventoryHistory
CREATE TABLE IF NOT EXISTS inventoryhistory (
    id         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id INTEGER NOT NULL,
    change     INTEGER NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    note       TEXT,
    CONSTRAINT fk_invh_prod FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- SupplierInventory
CREATE TABLE IF NOT EXISTS supplierinventory (
    supplier_id INTEGER NOT NULL,
    product_id  INTEGER NOT NULL,
    quantity    INTEGER NOT NULL DEFAULT 0,
    unit_price  NUMERIC(12,2) DEFAULT 0.0,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (supplier_id, product_id),
    CONSTRAINT fk_sinv_sup  FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_sinv_prod FOREIGN KEY (product_id)  REFERENCES products(id)  ON DELETE CASCADE ON UPDATE CASCADE
);
SQL
