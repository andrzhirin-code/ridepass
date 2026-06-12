import os
import fitz
import qrcode
import re
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "timesbd.ttf")

# Импорт функции отправки в Telegram
from database import send_telegram

def get_field_params(doc, field):
    """Читает fontsize и align из /DA и /Q поля."""
    xref = field._annot.xref
    
    # Размер шрифта из /DA
    da_tuple = doc.xref_get_key(xref, "DA")
    da_str = da_tuple[1] if da_tuple and len(da_tuple) > 1 else ""
    
    fontsize = 10.0
    m = re.search(r"([\d.]+)\s+Tf", da_str)
    if m:
        fontsize = float(m.group(1))
    
    # Выравнивание из /Q
    q_tuple = doc.xref_get_key(xref, "Q")
    q_val = int(q_tuple[1]) if q_tuple and q_tuple[1].isdigit() else 0
    
    align_map = {
        0: fitz.TEXT_ALIGN_LEFT,
        1: fitz.TEXT_ALIGN_CENTER,
        2: fitz.TEXT_ALIGN_RIGHT,
    }
    align = align_map.get(q_val, fitz.TEXT_ALIGN_LEFT)
    
    return fontsize, align

def get_field_color(doc, field):
    """Читает цвет текста из /DA строки поля."""
    xref = field._annot.xref
    da_tuple = doc.xref_get_key(xref, "DA")
    da_str = da_tuple[1] if da_tuple and len(da_tuple) > 1 else ""
    
    # RGB: "0.2 0.4 0.8 rg"
    m = re.search(r"([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+rg", da_str)
    if m:
        return (float(m.group(1)), float(m.group(2)), float(m.group(3)))
    
    # Grayscale: "0.5 g"
    m = re.search(r"([\d.]+)\s+g\b", da_str)
    if m:
        g = float(m.group(1))
        return (g, g, g)
    
    # CMYK: "0 0 1 0 k"
    m = re.search(r"([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+k", da_str)
    if m:
        c, mg, y, k = [float(m.group(i)) for i in range(1, 5)]
        return (
            (1-c)*(1-k),
            (1-mg)*(1-k),
            (1-y)*(1-k)
        )
    
    return (0, 0, 0)

def fill_order_template(data: dict) -> str:
    print("📝 fill_order_template: старт")
    
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(f"⚠️ Файл шрифта timesbd.ttf не найден! Загрузите его в папку проекта.")

    doc = fitz.open(TEMPLATE_PATH)
    page = doc.load_page(0)

    # 1. Регистрируем шрифт в документе
    font_name = "TimesNewRomanBold"
    page.insert_font(fontname=font_name, fontfile=FONT_PATH)

    field_mapping = {
        "record_number": str(data.get('passport_number', '')).replace("№", ""),
        "series": data.get('series_code', ''),
        "entry_number": data.get('entry_number', ''),
        "issue_date": str(data.get("issue_date", "")),
        "vehicle_type_vision": str(data.get("vehicle_type_vision", "")),
        "brand": str(data.get("brand", "")),
        "model": str(data.get("model", "")),
        "year": str(data.get("year", "")),
        "frame_number": str(data.get("frame_number", "")),
        "engine_number": str(data.get("engine_number", "")),
        "vehicle_type": "Спортинвентарь",
        "engine_capacity": str(data.get("engine_capacity", "")),
        "strokes": str(data.get("strokes", "")),
        "cooling": str(data.get("cooling", "")),
        "transmission": str(data.get("transmission", "")),
        "fuel_system": str(data.get("fuel_system", "")),
        "front_brake": str(data.get("front_brake", "")),
        "rear_brake": str(data.get("rear_brake", "")),
        "weight": str(data.get("weight", "")),
        "full_name": str(data.get("full_name", "")),
        "passport": str(data.get("passport", "")),
        "address": str(data.get("address", "")),
        "doc_hash": str(data.get("doc_hash", "")),
    }

    # 2. Собираем данные полей
    fields_data = []
    for field in page.widgets():
        name = field.field_name
        if name in field_mapping and field_mapping[name]:
            fontsize, align = get_field_params(doc, field)
            color = get_field_color(doc, field)
            
            rect = field.rect
            
            # Диагностика для record_number
            if name == "record_number":
                send_telegram(
                    f"[DEBUG] record_number\n"
                    f"rect.height = {rect.height:.1f}\n"
                    f"fontsize из /DA = {fontsize}\n"
                    f"color = {color}"
                )
            
            # Переопределяем размер для record_number
            if name == "record_number":
                fontsize = 14  # подбери нужный размер
            elif fontsize > rect.height:
                fontsize = rect.height * 0.75
            
            fields_data.append({
                "name": name,
                "rect": rect,
                "value": field_mapping[name],
                "color": color,
                "fontsize": fontsize,
                "align": align,
            })
            field.field_value = field_mapping[name]
            field.update()

    # 3. Закрепляем внешний вид и удаляем интерактивность
    doc.need_appearances(True)
    page.wrap_contents()

    # 4. Удаляем интерактивные поля (с предварительным сбором)
    widgets_to_delete = list(page.widgets())
    for field in widgets_to_delete:
        page.delete_widget(field)

    # 5. Рисуем текст поверх со своим шрифтом
    for fd in fields_data:
        rect = fd["rect"]
        # Базовая линия — низ rect с небольшим отступом
        baseline_y = rect.y1 - (rect.height * 0.2)
        point = fitz.Point(rect.x0 + 2, baseline_y)
        
        rc = page.insert_text(
            point,
            fd["value"],
            fontname=font_name,
            fontfile=FONT_PATH,
            fontsize=fd["fontsize"],
            color=fd["color"],
        )
        if rc < 0:
            send_telegram(f"⚠️ Не влезло: {fd['name']} | fontsize={fd['fontsize']}")

    # 6. QR-код
    w = float(page.rect.x1)
    qr_rect = fitz.Rect(w - 250, 200, w - 50, 400)
    verification_url = f"https://ridepass.onrender.com/check?code={data.get('entry_number', '')}"
    
    qr = qrcode.QRCode(box_size=15, border=1)
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_bytes = BytesIO()
    qr_img.save(qr_bytes, "PNG")
    qr_bytes.seek(0)
    
    page.insert_image(qr_rect, stream=qr_bytes)

    # 7. Запрет на выделение и копирование
    perm_mask = fitz.PDF_PERM_ACCESSIBILITY 

    output_path = os.path.join(BASE_DIR, f"order_{data.get('entry_number', 'temp')}.pdf")
    doc.save(
        output_path, 
        garbage=4, 
        deflate=True, 
        encryption=fitz.PDF_ENCRYPT_AES_256, 
        owner_pw=os.urandom(16).hex(), 
        permissions=perm_mask
    )
    doc.close()
    
    print(f"✅ Документ успешно сгенерирован и аппаратно заблокирован: {output_path}")
    return output_path
