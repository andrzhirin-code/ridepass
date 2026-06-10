import os
import hashlib
import uuid
import requests
import json

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def supabase_request(method, table, data=None, params=None):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    if method == "GET":
        response = requests.get(url, headers=HEADERS, params=params)
    elif method == "POST":
        response = requests.post(url, headers=HEADERS, json=data)
    elif method == "PATCH":
        response = requests.patch(url, headers=HEADERS, json=data, params=params)
    elif method == "DELETE":
        response = requests.delete(url, headers=HEADERS, params=params)
    else:
        return None
    
    if response.status_code >= 400:
        print(f"Supabase error: {response.status_code} - {response.text}")
        return None
    return response.json()

def generate_unique_number():
    response = supabase_request("GET", "orders", params={"select": "unique_doc_number", "order": "id.desc", "limit": 1})
    if response and response[0].get("unique_doc_number"):
        last_num = int(response[0]["unique_doc_number"][1:])
        new_num = last_num + 1
    else:
        new_num = 73
    return f"№{new_num:05d}"

def generate_doc_hash(data_snapshot):
    secret_salt = "RidePassSecretKey2024"
    unique_id = str(uuid.uuid4())
    hash_input = f"{data_snapshot}{secret_salt}{unique_id}".encode()
    return hashlib.sha256(hash_input).hexdigest()[:16].upper()

def add_user(user_id, referral_link):
    supabase_request("POST", "users", {"user_id": user_id, "referral_link": referral_link})

def get_user(user_id):
    response = supabase_request("GET", "users", params={"user_id": f"eq.{user_id}"})
    return response[0] if response else None

def update_user_balance(user_id, amount):
    user = get_user(user_id)
    if user:
        new_balance = user["balance"] + amount
        new_total = user["total_earned"] + amount
        supabase_request("PATCH", "users", {"balance": new_balance, "total_earned": new_total}, params={"user_id": f"eq.{user_id}"})

def add_order(order_data):
    response = supabase_request("POST", "orders", {
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
    })
    return response[0]["id"] if response else None

def get_order(order_id):
    response = supabase_request("GET", "orders", params={"id": f"eq.{order_id}"})
    return response[0] if response else None

def get_order_by_entry_number(entry_number):
    response = supabase_request("GET", "orders", params={"entry_number": f"eq.{entry_number}"})
    return response[0] if response else None

def update_order_status(order_id, status):
    supabase_request("PATCH", "orders", {"status": status}, params={"id": f"eq.{order_id}"})

def get_pending_orders():
    response = supabase_request("GET", "orders", params={"status": "eq.waiting_confirm"})
    return response if response else []
