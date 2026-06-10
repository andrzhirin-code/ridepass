import os
import hashlib
import uuid
import asyncio
import requests
import asyncpg
from typing import Optional, List, Dict, Any, Union

ADMIN_ID = 5171781123
BOT_TOKEN = "8223376010:AAEzIB8EZqZexiOv8bzhhJLyv7fwO2Afte4"

def send_telegram(text: str):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": ADMIN_ID, "text": text},
            timeout=5
        )
    except:
        pass

send_telegram("🚀 Бот запущен. Используем asyncpg + IPv4 Pooler")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    send_telegram("❌ Ошибка: DATABASE_URL не установлена!")
    raise ValueError("DATABASE_URL не установлена!")

send_telegram(f"🔗 DATABASE_URL получена (скрыто)")

async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)


# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================

async def generate_unique_number() -> str:
    send_telegram("🔄 generate_unique_number вызван")
    conn = None
    try:
        conn = await get_db_connection()
        row = await conn.fetchrow(
            "SELECT unique_doc_number FROM orders ORDER BY id DESC LIMIT 1"
        )
        send_telegram(f"📥 Последний номер в БД: {row['unique_doc_number'] if row else 'нет'}")
        
        if row and row["unique_doc_number"]:
            last_num_str = row["unique_doc_number"].replace("№", "")
            last_num = int(last_num_str)
            new_num = last_num + 1
        else:
            new_num = 73
    except Exception as e:
        send_telegram(f"❌ Ошибка generate_unique_number: {e}")
        new_num = 73
    finally:
        if conn:
            await conn.close()
        
    result = f"№{new_num:05d}"
    send_telegram(f"✅ Сгенерирован номер: {result}")
    return result

def generate_doc_hash(data_snapshot: Any) -> str:
    secret_salt = "RidePassSecretKey2024"
    unique_id = str(uuid.uuid4())
    hash_input = f"{data_snapshot}{secret_salt}{unique_id}".encode()
    return hashlib.sha256(hash_input).hexdigest()[:16].upper()


# ==========================================
# ПОЛЬЗОВАТЕЛИ
# ==========================================

async def add_user(user_id: Union[int, str], referral_link: str) -> None:
    send_telegram(f"🔄 add_user: {user_id}")
    conn = None
    try:
        conn = await get_db_connection()
        await conn.execute(
            "INSERT INTO users (user_id, referral_link) VALUES ($1, $2) ON CONFLICT (user_id) DO NOTHING",
            int(user_id), referral_link
        )
        send_telegram(f"✅ add_user успешно: {user_id}")
    except Exception as e:
        send_telegram(f"❌ Ошибка add_user: {e}")
    finally:
        if conn:
            await conn.close()

async def get_user(user_id: Union[int, str]) -> Optional[Dict[str, Any]]:
    send_telegram(f"🔄 get_user: {user_id}")
    conn = None
    try:
        conn = await get_db_connection()
        row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", int(user_id))
        result = dict(row) if row else None
        send_telegram(f"📥 get_user результат: {'найден' if result else 'не найден'}")
        return result
    except Exception as e:
        send_telegram(f"❌ Ошибка get_user: {e}")
        return None
    finally:
        if conn:
            await conn.close()

async def update_user_balance(user_id: Union[int, str], amount: float) -> None:
    send_telegram(f"🔄 update_user_balance: {user_id}, {amount}")
    user = await get_user(user_id)
    if not user:
        send_telegram(f"❌ Пользователь {user_id} не найден")
        return

    new_balance = float(user.get("balance", 0)) + float(amount)
    new_total = float(user.get("total_earned", 0)) + float(amount)
    
    conn = None
    try:
        conn = await get_db_connection()
        await conn.execute(
            "UPDATE users SET balance = $1, total_earned = $2 WHERE user_id = $3",
            new_balance, new_total, int(user_id)
        )
        send_telegram(f"✅ update_user_balance успешно")
    except Exception as e:
        send_telegram(f"❌ Ошибка update_user_balance: {e}")
    finally:
        if conn:
            await conn.close()


# ==========================================
# ЗАКАЗЫ
# ==========================================

async def add_order(order_data: tuple) -> Optional[int]:
    send_telegram(f"🔄 add_order: длина кортежа {len(order_data)}")
    send_telegram(f"📦 Данные (первые 5): {order_data[:5]}")
    
    conn = None
    try:
        conn = await get_db_connection()
        
        query = """
            INSERT INTO orders (
                user_id, unique_doc_number, doc_hash, series, issue_date, entry_number,
                vehicle_type_vision, brand, model, year, frame_number, engine_number,
                vehicle_type_static, engine_capacity, strokes, cooling, transmission,
                fuel_system, front_brake, rear_brake, weight, full_name, passport, address
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, $24
            ) RETURNING id
        """
        
        order_id = await conn.fetchval(query, *order_data)
        
        if order_id:
            send_telegram(f"✅ Заказ создан! ID: {order_id}")
            return order_id
        else:
            send_telegram(f"❌ Ошибка: база не вернула ID")
            return None
            
    except IndexError as e:
        send_telegram(f"❌ IndexError в add_order: {e}, длина {len(order_data)}")
        return None
    except Exception as e:
        send_telegram(f"❌ Ошибка add_order: {e}")
        return None
    finally:
        if conn:
            await conn.close()

async def get_order(order_id: Union[int, str]) -> Optional[Dict[str, Any]]:
    send_telegram(f"🔄 get_order: {order_id}")
    conn = None
    try:
        conn = await get_db_connection()
        row = await conn.fetchrow("SELECT * FROM orders WHERE id = $1", int(order_id))
        result = dict(row) if row else None
        send_telegram(f"📥 get_order: {'найден' if result else 'не найден'}")
        return result
    except Exception as e:
        send_telegram(f"❌ Ошибка get_order: {e}")
        return None
    finally:
        if conn:
            await conn.close()

async def get_order_by_entry_number(entry_number: str) -> Optional[Dict[str, Any]]:
    send_telegram(f"🔄 get_order_by_entry_number: {entry_number}")
    conn = None
    try:
        conn = await get_db_connection()
        row = await conn.fetchrow("SELECT * FROM orders WHERE entry_number = $1", str(entry_number))
        result = dict(row) if row else None
        send_telegram(f"📥 get_order_by_entry_number: {'найден' if result else 'не найден'}")
        return result
    except Exception as e:
        send_telegram(f"❌ Ошибка get_order_by_entry_number: {e}")
        return None
    finally:
        if conn:
            await conn.close()

async def update_order_status(order_id: Union[int, str], status: str) -> None:
    send_telegram(f"🔄 update_order_status: {order_id} -> {status}")
    conn = None
    try:
        conn = await get_db_connection()
        await conn.execute("UPDATE orders SET status = $1 WHERE id = $2", str(status), int(order_id))
        send_telegram(f"✅ update_order_status успешно")
    except Exception as e:
        send_telegram(f"❌ Ошибка update_order_status: {e}")
    finally:
        if conn:
            await conn.close()

async def get_pending_orders() -> List[Dict[str, Any]]:
    send_telegram("🔄 get_pending_orders")
    conn = None
    try:
        conn = await get_db_connection()
        rows = await conn.fetch("SELECT * FROM orders WHERE status = 'waiting_confirm'")
        result = [dict(r) for r in rows] if rows else []
        send_telegram(f"📥 Найдено ожидающих заказов: {len(result)}")
        return result
    except Exception as e:
        send_telegram(f"❌ Ошибка get_pending_orders: {e}")
        return []
    finally:
        if conn:
            await conn.close()
