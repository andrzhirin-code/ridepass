import sqlite3
import hashlib
import os

DB_NAME = "ridepass.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    # ... (таблица users без изменений) ...
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
            unique_doc_number TEXT UNIQUE,
            doc_hash TEXT UNIQUE,
            -- Все поля из вашей анкеты
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
            -- Служебные поля
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Функция для генерации уникального номера (№ паспорта мототехники)
def generate_unique_number():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    # Находим последний использованный номер
    cur.execute("SELECT unique_doc_number FROM orders WHERE unique_doc_number IS NOT NULL ORDER BY id DESC LIMIT 1")
    last = cur.fetchone()
    conn.close()
    
    if last:
        # Извлекаем число из формата "№00073" и увеличиваем на 1
        last_num = int(last[0][1:])  # убираем '№'
        new_num = last_num + 1
    else:
        new_num = 73  # Стартуем с 73, как ты и хотел
    return f"№{new_num:05d}"  # Форматируем в "№00073"

# Функция для генерации хеша документа
def generate_doc_hash(data_snapshot):
    secret_salt = "MySuperSecretRidePassSalt2024"
    hash_input = f"{data_snapshot}{secret_salt}".encode()
    return hashlib.sha256(hash_input).hexdigest()[:16].upper()
