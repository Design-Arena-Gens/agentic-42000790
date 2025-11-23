-- Core tables
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash BLOB NOT NULL,
    role_code TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS roles (
    code TEXT PRIMARY KEY,
    label TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    entity TEXT,
    entity_id INTEGER,
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Business entities
CREATE TABLE IF NOT EXISTS partners (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL CHECK (kind IN ('client','supplier')),
    name_fr TEXT NOT NULL,
    name_ar TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    email TEXT DEFAULT '',
    address TEXT DEFAULT '',
    tax_id TEXT DEFAULT '',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    name_fr TEXT NOT NULL,
    name_ar TEXT DEFAULT '',
    unit TEXT DEFAULT 'u',
    price_ht REAL NOT NULL DEFAULT 0,
    vat_rate REAL NOT NULL DEFAULT 20.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stock (
    product_id INTEGER PRIMARY KEY,
    qty REAL NOT NULL DEFAULT 0,
    FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS stock_moves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    qty REAL NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('in','out')),
    reference TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Sales docs
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL CHECK (kind IN ('quote','delivery','invoice','purchase')),
    number TEXT NOT NULL UNIQUE,
    partner_id INTEGER,
    date TEXT NOT NULL,
    total_ht REAL NOT NULL DEFAULT 0,
    total_tva REAL NOT NULL DEFAULT 0,
    total_ttc REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'draft',
    notes TEXT DEFAULT '',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(partner_id) REFERENCES partners(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS document_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    product_id INTEGER,
    description TEXT NOT NULL,
    qty REAL NOT NULL DEFAULT 1,
    unit_price REAL NOT NULL DEFAULT 0,
    vat_rate REAL NOT NULL DEFAULT 20.0,
    total_ht REAL NOT NULL DEFAULT 0,
    total_tva REAL NOT NULL DEFAULT 0,
    total_ttc REAL NOT NULL DEFAULT 0,
    FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    method TEXT NOT NULL DEFAULT 'cash',
    amount REAL NOT NULL,
    paid_at TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS cash_register (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movement TEXT NOT NULL CHECK (movement IN ('in','out')),
    amount REAL NOT NULL,
    label TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

