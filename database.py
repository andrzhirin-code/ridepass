import sqlite3
import hashlib
import os

DB_NAME = "ridepass.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Таблица пользователей
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
    
    # Таблица заявок с новыми полями
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            unique_doc_number TEXT UNIQUE,
            doc_hash TEXT UNIQUE,
            series TEXT,
            issue_date TEXT,
            entry_number TEXT UNIQUE,
            vehicle_type_vision TEXT,
            brand TEXT,
            model TEXT,
            year TEXT,
            frame_number TEXT,
            engine_number TEXT,
            vehicle_type_static TEXT,
            engine_capacity TEXT,
            strokes TEXT,
            cooling TEXT,
            transmission TEXT,
            fuel_system TEXT,
            front_brake TEXT,
            rear_brake TEXT,
            weight TEXT,
            full_name TEXT,
            passport TEXT,
            address TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def generate_unique_number():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT unique_doc_number FROM orders WHERE unique_doc_number IS NOT NULL ORDER BY id DESC LIMIT 1")
    last = cur.fetchone()
    conn.close()
    
    if last:
        last_num = int(last[0][1:])
        new_num = last_num + 1
    else:
        new_num = 73
    return f"№{new_num:05d}"

def generate_doc_hash(data_snapshot):
    secret_salt = "RidePassSecretKey2024"
    hash_input = f"{data_snapshot}{secret_salt}".encode()
    return hashlib.sha256(hash_input).hexdigest()[:16].upper()

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
        INSERT INTO orders (
            user_id, unique_doc_number, doc_hash, series, issue_date, entry_number,
            vehicle_type_vision, brand, model, year, frame_number, engine_number,
            vehicle_type_static, engine_capacity, strokes, cooling, transmission,
            fuel_system, front_brake, rear_brake, weight, full_name, passport, address
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

def get_order_by_entry_number(entry_number):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE entry_number = ?", (entry_number,))
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
