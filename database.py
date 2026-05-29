import sqlite3

DB_NAME = "ridepass.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            referral_link TEXT,
            balance INTEGER DEFAULT 0,
            total_earned INTEGER DEFAULT 0,
            referrals_count INTEGER DEFAULT 0,
            paid_referrals INTEGER DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            vehicle_type TEXT,
            brand TEXT,
            model TEXT,
            year TEXT,
            power TEXT,
            serial TEXT,
            full_name TEXT,
            passport TEXT,
            address TEXT,
            phone TEXT,
            speed TEXT,
            status TEXT DEFAULT 'waiting_payment',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id, referral_link):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, referral_link) VALUES (?, ?)", (user_id, referral_link))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user

def update_user_balance(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance = balance + ?, total_earned = total_earned + ? WHERE user_id = ?", (amount, amount, user_id))
    conn.commit()
    conn.close()

def add_order(order_data):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (user_id, vehicle_type, brand, model, year, power, serial, full_name, passport, address, phone, speed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, order_data)
    order_id = cur.lastrowid
    conn.commit()
    conn.close()
    return order_id

def get_order(order_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order = cur.fetchone()
    conn.close()
    return order

def update_order_status(order_id, status):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()

def get_pending_orders():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE status = 'waiting_confirm'")
    orders = cur.fetchall()
    conn.close()
    return orders
