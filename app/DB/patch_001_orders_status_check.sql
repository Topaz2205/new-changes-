PRAGMA foreign_keys = OFF;

BEGIN TRANSACTION;

-- 1) Rename old table
ALTER TABLE Orders RENAME TO Orders__bak;

-- 2) Recreate Orders with CHECK on status (Option A)
CREATE TABLE Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    employee_id INTEGER,
    status TEXT NOT NULL CHECK (status IN ('NEW','PAID','SHIPPED','DELIVERED','CANCELLED')),
    total_amount REAL,
    freight REAL,
    ship_via TEXT,
    expected_delivery DATETIME,
    actual_delivery DATETIME,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    shipped_date DATETIME,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)     REFERENCES Users(id),
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
    FOREIGN KEY (employee_id) REFERENCES Employees(id)
);

-- 3) Copy data that complies with the new CHECK
INSERT INTO Orders (
  order_id, user_id, customer_id, employee_id, status, total_amount, freight, ship_via,
  expected_delivery, actual_delivery, order_date, shipped_date, updated_at
)
SELECT
  order_id, user_id, customer_id, employee_id,
  UPPER(status) as status,
  total_amount, freight, ship_via,
  expected_delivery, actual_delivery, order_date, shipped_date, updated_at
FROM Orders__bak
WHERE UPPER(status) IN ('NEW','PAID','SHIPPED','DELIVERED','CANCELLED');

-- 4) Drop old table
DROP TABLE Orders__bak;

-- 5) Helpful index for status
CREATE INDEX IF NOT EXISTS idx_orders_status ON Orders(status);

COMMIT;

PRAGMA foreign_keys = ON;
