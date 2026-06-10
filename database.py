import os
import hashlib
import uuid
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_unique_number():
    response = supabase.table("orders").select("unique_doc_number").order("id", desc=True).limit(1).execute()
    if response.data and response.data[0]["unique_doc_number"]:
        last_num = int(response.data[0]["unique_doc_number"][1:])
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
    supabase.table("users").upsert({"user_id": user_id, "referral_link": referral_link}).execute()

def get_user(user_id):
    response = supabase.table("users").select("*").eq("user_id", user_id).execute()
    return response.data[0] if response.data else None

def update_user_balance(user_id, amount):
    user = get_user(user_id)
    if user:
        new_balance = user["balance"] + amount
        new_total = user["total_earned"] + amount
        supabase.table("users").update({
            "balance": new_balance,
            "total_earned": new_total,
            "referrals_count": user.get("referrals_count", 0),
            "paid_referrals": user.get("paid_referrals", 0)
        }).eq("user_id", user_id).execute()

def add_order(order_data):
    try:
        response = supabase.table("orders").insert({
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
        }).execute()
        return response.data[0]["id"] if response.data else None
    except Exception as e:
        print(f"Ошибка add_order: {e}")
        return None

def get_order(order_id):
    response = supabase.table("orders").select("*").eq("id", order_id).execute()
    return response.data[0] if response.data else None

def get_order_by_entry_number(entry_number):
    response = supabase.table("orders").select("*").eq("entry_number", entry_number).execute()
    return response.data[0] if response.data else None

def update_order_status(order_id, status):
    supabase.table("orders").update({"status": status}).eq("id", order_id).execute()

def get_pending_orders():
    response = supabase.table("orders").select("*").eq("status", "waiting_confirm").execute()
    return response.data
