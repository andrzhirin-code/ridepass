import os
import hashlib
import uuid
import aiohttp
from typing import Optional, Union, Any, List

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

BASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

async def supabase_request(method: str, table: str, data: dict = None, params: dict = None) -> Optional[Union[dict, list]]:
    connector = aiohttp.TCPConnector(family=aiohttp.resolver.socket.AF_INET)
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    
    headers = BASE_HEADERS.copy()
    if method in ("POST", "PATCH"):
        headers["Prefer"] = "return=representation"
    
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        try:
            if method == "GET":
                async with session.get(url, params=params) as resp:
                    res_body = await resp.json()
                    if resp.status >= 400:
                        print(f"🛑 [Supabase API Error] Status {resp.status}: {res_body}")
                    return res_body
            elif method == "POST":
                async with session.post(url, json=data, params=params) as resp:
                    res_body = await resp.json()
                    if resp.status >= 400:
                        print(f"🛑 [Supabase API Error] Status {resp.status}: {res_body}")
                    return res_body
            elif method == "PATCH":
                async with session.patch(url, json=data, params=params) as resp:
                    res_body = await resp.json()
                    if resp.status >= 400:
                        print(f"🛑 [Supabase API Error] Status {resp.status}: {res_body}")
                    return res_body
        except Exception as e:
            print(f"❌ [Network/Python Error] Исключение при запросе {method} к {table}: {e}")
            return None

async def generate_unique_number() -> str:
    response = await supabase_request("GET", "orders", params={"select": "unique_doc_number", "order": "id.desc", "limit": 1})
    if response and isinstance(response, list) and response[0].get("unique_doc_number"):
        try:
            last_num_str = response[0]["unique_doc_number"].replace("№", "")
            last_num = int(last_num_str)
            new_num = last_num + 1
        except (ValueError, IndexError):
            new_num = 73
    else:
        new_num = 73
    return f"№{new_num:05d}"

def generate_doc_hash(data_snapshot: Any) -> str:
    secret_salt = "RidePassSecretKey2024"
    unique_id = str(uuid.uuid4())
    hash_input = f"{data_snapshot}{secret_salt}{unique_id}".encode()
    return hashlib.sha256(hash_input).hexdigest()[:16].upper()

async def add_user(user_id: int, referral_link: str) -> None:
    await supabase_request("POST", "users", {"user_id": user_id, "referral_link": referral_link})

async def get_user(user_id: int) -> Optional[dict]:
    response = await supabase_request("GET", "users", params={"user_id": f"eq.{user_id}"})
    return response[0] if response and isinstance(response, list) else None

async def update_user_balance(user_id: int, amount: float) -> None:
    user = await get_user(user_id)
    if user:
        new_balance = user.get("balance", 0) + amount
        new_total = user.get("total_earned", 0) + amount
        await supabase_request("PATCH", "users", {"balance": new_balance, "total_earned": new_total}, params={"user_id": f"eq.{user_id}"})

async def add_order(order_data: tuple) -> Optional[int]:
    print(f"🔄 DEBUG: Вызов add_order. Получено элементов в кортеже: {len(order_data)}")
    
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
        print(f"❌ DEBUG: Ошибка индексов кортежа! Передано {len(order_data)} элементов, ожидалось 24. Ошибка: {e}")
        return None

    response = await supabase_request("POST", "orders", payload)
    print(f"📥 DEBUG: Получен ответ базы данных: {response}")
    
    if response and isinstance(response, list) and len(response) > 0:
        order_id = response[0].get("id")
        print(f"✅ DEBUG: Заказ успешно создан! ID: {order_id}")
        return order_id
    else:
        print("❌ DEBUG: Не удалось создать заказ. Ответ пустой или словарь ошибки.")
        return None

async def get_order(order_id: int) -> Optional[dict]:
    response = await supabase_request("GET", "orders", params={"id": f"eq.{order_id}"})
    return response[0] if response and isinstance(response, list) else None

async def get_order_by_entry_number(entry_number: str) -> Optional[dict]:
    response = await supabase_request("GET", "orders", params={"entry_number": f"eq.{entry_number}"})
    return response[0] if response and isinstance(response, list) else None

async def update_order_status(order_id: int, status: str) -> None:
    await supabase_request("PATCH", "orders", {"status": status}, params={"id": f"eq.{order_id}"})

async def get_pending_orders() -> List[dict]:
    response = await supabase_request("GET", "orders", params={"status": "eq.waiting_confirm"})
    return response if response and isinstance(response, list) else []
