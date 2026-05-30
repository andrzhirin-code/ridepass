import os
import fitz
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
ADMIN_ID = 5171781123
BOT_TOKEN = "8223376010:AAEzIB8EZqZexiOv8bzhhJLyv7fwO2Afte4"

def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": ADMIN_ID, "text": text})

def fill_order_template(data: dict) -> str:
    doc = fitz.open(TEMPLATE_PATH)
    page = doc[0]
    
    widgets = list(page.widgets())
    msg = f"Виджетов: {len(widgets)}\n"
    for w in widgets:
        msg += f"Поле: {w.field_name}\n"
    
    # Отправляем в Telegram
    send_telegram(msg)
    
    output_path = os.path.join(BASE_DIR, f"debug.pdf")
    doc.save(output_path)
    doc.close()
    return output_path
