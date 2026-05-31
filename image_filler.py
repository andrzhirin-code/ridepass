import os
import requests
from pypdf import PdfReader, PdfWriter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
ADMIN_ID = 5171781123
BOT_TOKEN = "8223376010:AAEzIB8EZqZexiOv8bzhhJLyv7fwO2Afte4"

def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": ADMIN_ID, "text": text})

def fill_order_template(data: dict) -> str:
    # Диагностика: какие поля в шаблоне
    reader = PdfReader(TEMPLATE_PATH)
    fields = reader.get_fields()
    field_names = list(fields.keys()) if fields else []
    send_telegram(f"🔍 Поля в шаблоне: {field_names}")

    writer = PdfWriter()
    writer.append(reader)

    values = {
        "vehicle_type": str(data.get("vehicle_type", "")),
        "category": "СИМ",
        "brand": str(data.get("brand", "")),
        "model": str(data.get("model", "")),
        "year": str(data.get("year", "")),
        "vin": str(data.get("vin", "")),
        "power": str(data.get("power", "")),
        "max_speed": str(data.get("max_speed", "")),
        "full_name": str(data.get("full_name", "")),
        "passport": str(data.get("passport", "")),
        "address": str(data.get("address", "")),
        "id": str(data.get("id", "")),
    }

    writer.update_page_form_field_values(writer.pages[0], values)

    output_path = os.path.join(BASE_DIR, f"order_{data.get('id', '1')}.pdf")
    with open(output_path, "wb") as f:
        writer.write(f)

    # Диагностика: что записалось
    check = PdfReader(output_path)
    filled = check.get_fields()
    if filled:
        for k, v in filled.items():
            send_telegram(f"📦 {k} = {v.get('/V', 'empty')}")
    else:
        send_telegram("❌ Поля не найдены после записи")

    return output_path
