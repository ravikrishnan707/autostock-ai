
-- AutoStock AI Database Schema

-- 1. Spare parts
CREATE TABLE IF NOT EXISTS parts (
    part_id TEXT PRIMARY KEY,
    part_name TEXT NOT NULL,
    unit_cost REAL NOT NULL CHECK (unit_cost >= 0)
);

-- 2. Warehouses
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,
    warehouse_name TEXT NOT NULL UNIQUE,
    location TEXT
);

-- 3. Suppliers
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_name TEXT NOT NULL UNIQUE,
    lead_time_days INTEGER NOT NULL CHECK (lead_time_days > 0)
);

-- 4. Inventory: stock of each part at each warehouse
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_id TEXT NOT NULL,
    warehouse_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    stock INTEGER NOT NULL CHECK (stock >= 0),
    daily_demand REAL NOT NULL CHECK (daily_demand > 0),
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (part_id) REFERENCES parts(part_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),

    UNIQUE (part_id, warehouse_id)
);

-- 5. Daily sales history
CREATE TABLE IF NOT EXISTS sales_history (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_id TEXT NOT NULL,
    warehouse_id INTEGER NOT NULL,
    sale_date TEXT NOT NULL,
    units_sold INTEGER NOT NULL CHECK (units_sold >= 0),

    FOREIGN KEY (part_id) REFERENCES parts(part_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),

    UNIQUE (part_id, warehouse_id, sale_date)
);

-- 6. Purchase orders
CREATE TABLE IF NOT EXISTS purchase_orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_id TEXT NOT NULL,
    warehouse_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    order_date TEXT NOT NULL,
    expected_delivery_date TEXT,
    status TEXT NOT NULL DEFAULT 'Pending'
        CHECK (status IN ('Pending', 'Approved', 'Shipped', 'Delivered', 'Cancelled')),

    FOREIGN KEY (part_id) REFERENCES parts(part_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);
