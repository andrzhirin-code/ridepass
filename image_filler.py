from PIL import Image, ImageDraw, ImageFont
import os

def generate_pdf(order_data):
    template_path = "template.png"
    
    # Если нет шаблона — создаём простой PDF
    if not os.path.exists(template_path):
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=12)
        for key, value in order_data.items():
            pdf.cell(0, 10, f"{key}: {value}", ln=True)
        output_path = f"temp_{order_data.get('id', 'unknown')}.pdf"
        pdf.output(output_path)
        return output_path
    
    # Открываем шаблон
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    # Загружаем шрифт (Arial, размер 14)
    try:
        font = ImageFont.truetype("arial.ttf", 14)
        font_bold = ImageFont.truetype("arialbd.ttf", 14)
    except:
        font = ImageFont.load_default()
        font_bold = font
    
    # Получаем размер изображения (для отладки)
    width, height = img.size
    print(f"Размер шаблона: {width}x{height}")
    
    # ========== КООРДИНАТЫ ДЛЯ ЗАПОЛНЕНИЯ (подбираются под твой template.png) ==========
    # Все координаты указаны в пикселях (X, Y)
    # При первом запуске они могут немного смещаться — поправим позже
    
    fields = {
        # Шапка таблицы (Серия RP, ID, № записи)
        'series_rp': (150, 200),
        'doc_id': (350, 200),
        'record_number': (550, 200),
        
        # Раздел I. ОСНОВНЫЕ ДАННЫЕ (Y увеличивается с каждым полем)
        'vehicle_type': (200, 400),   # 1. Тип транспортного средства
        # Категория — всегда "СИМ", заполняем автоматически
        'brand': (200, 470),          # 3. Марка
        'model': (200, 540),          # 4. Модель
        'year': (200, 610),           # 5. Год выпуска
        'serial': (200, 680),         # 6. Идентификационный номер
        'power': (200, 750),          # 7. Мощность двигателя
        'speed': (200, 820),          # 8. Максимальная скорость
        
        # Раздел II. ДАННЫЕ О ВЛАДЕЛЬЦЕ
        'full_name': (250, 950),      # 1. ФИО
        'passport': (200, 1020),      # 2. Паспорт
        'address': (200, 1090),       # 3. Адрес
        
        # Раздел III. СРОК ДЕЙСТВИЯ
        'issue_date': (200, 1220),    # Дата выдачи
        'expiry_date': (400, 1220),   # Действительна до
        
        # Раздел V. СВЕДЕНИЯ О ДОКУМЕНТЕ
        'registry_number': (200, 1450),  # Реестровый номер
        'doc_hash': (550, 1450),         # Хеш документа
        # Дата формирования (берём ту же issue_date)
    }
    
    # Заполняем поля
    for field_name, (x, y) in fields.items():
        value = order_data.get(field_name, '')
        if value:
            draw.text((x, y), str(value), fill="black", font=font)
    
    # Категория — всегда "СИМ"
    draw.text((200, 440), "СИМ", fill="black", font=font)
    
    # Дата формирования (раздел V) — используем issue_date
    if 'issue_date' in order_data:
        draw.text((400, 1450), order_data['issue_date'], fill="black", font=font)
    
    # Сохраняем как PDF
    output_path = f"temp_{order_data.get('id', 'unknown')}.pdf"
    img.save(output_path, "PDF", resolution=100.0)
    print(f"PDF сохранён: {output_path}")
    return output_path
