
SELECT DISTINCT status FROM orders ORDER BY 1;

-- להוסיף CHECK בלי לשבור אם יש ערכים לא תקינים:
ALTER TABLE orders
  ADD CONSTRAINT orders_status_chk
  CHECK (status IN ('NEW','PAID','SHIPPED','DELIVERED','CANCELLED')) NOT VALID;

-- לאשר את ה-constraint (יזרוק שגיאה אם יש ערכים לא חוקיים):
ALTER TABLE orders VALIDATE CONSTRAINT orders_status_chk;
