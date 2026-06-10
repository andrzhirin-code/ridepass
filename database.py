import os
import socket
import hashlib
import uuid
import asyncio
import requests
from typing import Optional, List, Dict, Any, Union
from supabase import create_client, Client

# ==========================================
# ОТПРАВКА ДИАГНОСТИКИ В TELEGRAM
# ==========================================
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

send_telegram("🚀 Бот запущен. Database.py загружен, DNS патч применён.")

# ==========================================
# ФИКС DNS ДЛЯ RENDER (IPv4 ONLY)
# ==========================================
orig_getaddrinfo = socket.getaddrinfo

def ipv4_only_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

socket.getaddrinfo = ipv4_only_getaddrinfo

send_telegram("✅ DNS патч IPv4 применён")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    send_telegram("❌ Ошибка: SUPABASE_URL или SUPABASE_KEY не установлены!")
    raise ValueError("SUPABASE_URL или SUPABASE_KEY не установлены!")

send_telegram(f"🔗 SUPABASE_URL: {SUPABASE_URL}")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    send_telegram("✅ Клиент Supabase создан успешно")
except Exception as e:
    send_telegram(f"❌ Ошибка создания клиента Supabase: {e}")
    raise e


# ==========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================

async def generate_unique_number() -> str:
    send_telegram("🔄 generate_unique_number вызван")
    def _sync_query():
        return supabase.table("orders").select("unique_doc_number").order("id", desc=True).limit(1).execute()
        
    try:
        response = await asyncio.to_thread(_sync_query)
        send_telegram(f"📥 Ответ generate_unique_number: {response.data}")
        if response.data and len(response.data) > 0 and response.data[0].get("unique_doc_number"):
            last_num_str = response.data[0].get("unique_doc_number", "").replace("№", "")
            last_num = int(last_num_str)
            new_num = last_num + 1
        else:
            new_num = 73
    except Exception as e:
        send_telegram(f"❌ Ошибка generate_unique_number: {e}")
        new_num = 73
        
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
    def _sync_query():
        return supabase.table("users").insert({"user_id": int(user_id), "referral_link": referral_link}).execute()
        
    try:
        await asyncio.to_thread(_sync_query)
        send_telegram(f"✅ add_user успешно: {user_id}")
    except Exception as e:
        send_telegram(f"❌ Ошибка add_user: {e}")

async def get_user(user_id: Union[int, str]) -> Optional[Dict[str, Any]]:
    send_telegram(f"🔄 get_user: {user_id}")
    def _sync_query():
        return supabase.table("users").select("*").eq("user_id", int(user_id)).execute()
        
    try:
        response = await asyncio.to_thread(_sync_query)
        result = response.data[0] if response.data and len(response.data) > 0 else None
        send_telegram(f"📥 get_user результат: {result is not None}")
        return result
    except Exception as e:
        send_telegram(f"❌ Ошибка get_user: {e}")
        return None

async def update_user_balance(user_id: Union[int, str], amount: float) -> None:
    send_telegram(f"🔄 update_user_balance: {user_id}, {amount}")
    user = await get_user(user_id)
    if not user:
        send_telegram(f"❌ Пользователь {user_id} не найден")
        return

    new_balance = float(user.get("balance", 0)) + float(amount)
    new_total = float(user.get("total_earned", 0)) + float(amount)
    
    def _sync_query():
        return supabase.table("users").update({"balance": new_balance, "total_earned": new_total}).eq("user_id", int(user_id)).execute()
        
    try:
        await asyncio.to_thread(_sync_query)
        send_telegram(f"✅ update_user_balance успешно")
    except Exception as e:
        send_telegram(f"❌ Ошибка update_user_balance: {e}")


# ==========================================
# ЗАКАЗЫ
# ==========================================

async def add_order(order_data: tuple) -> Optional[int]:
    send_telegram(f"🔄 add_order: длина кортежа {len(order_data)}")
    send_telegram(f"📦 Данные (первые 5): {order_data[:5]}")
    
    try:
        payload = {
            "user_id": order_data[0],
            "unique_doc_number": order_data[1],
            "doc_hash": order_data[2],
            "series": order_data[3],
            "issue_date": order_data[4],
            "entry_number": order_data[5],
            "vehicle_type_vision": order_data[6],
            "brand": order_data[7],
            "model": order_data[8],
            "year": order_data[9],
            "frame_number": order_data[10],
            "engine_number": order_data[11],
            "vehicle_type_static": order_data[12],
            "engine_capacity": order_data[13],
            "strokes": order_data[14],
            "cooling": order_data[15],
            "transmission": order_data[16],
            "fuel_system": order_data[17],
            "front_brake": order_data[18],
            "rear_brake": order_data[19],
            "weight": order_data[20],
            "full_name": order_data[21],
            "passport": order_data[22],
            "address": order_data[23],
        }
    except IndexError as e:
        send_telegram(f"❌ IndexError в add_order: {e}, длина {len(order_data)}")
        return None

    def _sync_query():
        return supabase.table("orders").insert(payload).execute()
        
    try:
        response = await asyncio.to_thread(_sync_query)
        send_telegram(f"📥 Ответ Supabase: {response.data}")
        if response.data and len(response.data) > 0:
            order_id = response.data[0].get("id")
            send_telegram(f"✅ Заказ создан! ID: {order_id}")
            return order_id
        else:
            send_telegram(f"❌ Пустой ответ от Supabase")
            return None
    except Exception as e:
        send_telegram(f"❌ Ошибка add_order: {e}")
        return None

async def get_order(order_id: Union[int, str]) -> Optional[Dict[str, Any]]:
    send_telegram(f"🔄 get_order: {order_id}")
    def _sync_query():
        return supabase.table("orders").select("*").eq("id", int(order_id)).execute()
        
    try:
        response = await asyncio.to_thread(_sync_query)
        result = response.data[0] if response.data and len(response.data) > 0 else None
        send_telegram(f"📥 get_order: {'найден' if result else 'не найден'}")
        return result
    except Exception as e:
        send_telegram(f"❌ Ошибка get_order: {e}")
        return None

async def get_order_by_entry_number(entry_number: str) -> Optional[Dict[str, Any]]:
    send_telegram(f"🔄 get_order_by_entry_number: {entry_number}")
    def _sync_query():
        return supabase.table("orders").select("*").eq("entry_number", str(entry_number)).execute()
        
    try:
        response = await asyncio.to_thread(_sync_query)
        result = response.data[0] if response.data and len(response.data) > 0 else None
        send_telegram(f"📥 get_order_by_entry_number: {'найден' if result else 'не найден'}")
        return result
    except Exception as e:
        send_telegram(f"❌ Ошибка get_order_by_entry_number: {e}")
        return None

async def update_order_status(order_id: Union[int, str], status: str) -> None:
    send_telegram(f"🔄 update_order_status: {order_id} -> {status}")
    def _sync_query():
        return supabase.table("orders").update({"status": str(status)}).eq("id", int(order_id)).execute()
        
    try:
        await asyncio.to_thread(_sync_query)
        send_telegram(f"✅ update_order_status успешно")
    except Exception as e:
        send_telegram(f"❌ Ошибка update_order_status: {e}")

async def get_pending_orders() -> List[Dict[str, Any]]:
    send_telegram("🔄 get_pending_orders вызван")
    def _sync_query():
        return supabase.table("orders").select("*").eq("status", "waiting_confirm").execute()
        
    try:
        response = await asyncio.to_thread(_sync_query)
        count = len(response.data) if response.data else 0
        send_telegram(f"📥 get_pending_orders: найдено {count} заявок")
        return response.data if response.data else []
    except Exception as e:
        send_telegram(f"❌ Ошибка get_pending_orders: {e}")
        return []
