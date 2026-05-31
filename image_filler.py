import fitz
import requests

ADMIN_ID = 5171781123
BOT_TOKEN = "8223376010:AAEzIB8EZqZexiOv8bzhhJLyv7fwO2Afte4"

def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": ADMIN_ID, "text": text})

doc = fitz.open("template_form.pdf")
page = doc[0]

widgets = sorted(page.widgets(), key=lambda w: (round(w.rect.y0), round(w.rect.x0)))

msg = "--- СПИСОК ПОЛЕЙ В PDF ---\n"
for i, w in enumerate(widgets, 1):
    msg += f"Поле {i}: Имя = '{w.field_name}'\n"

send_telegram(msg)
