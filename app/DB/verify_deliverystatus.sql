-- Ensure DeliveryStatus table exists with expected columns
CREATE TABLE IF NOT EXISTS DeliveryStatus (
    status_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    delay_reason TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);

-- Optional helpful index
CREATE INDEX IF NOT EXISTS idx_deliverystatus_order ON DeliveryStatus(order_id);
