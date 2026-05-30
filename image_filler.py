from PIL import Image, ImageDraw, ImageFont
import os

def generate_pdf(order_data):
    template_path = "template.png"
    
    # Если нет шаблона — создаём PDF через fpdf2
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
    
    # Загружаем БОЛЬШОЙ шрифт (24 пикселя)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
        font_bold = ImageFont.truetype("arialbd.ttf", 24)
    except:
        font = ImageFont.load_default()
        font_bold = font
    
    # Получаем размеры картинки
    width, height = img.size
    print(f"Размер шаблона: {width}x{height}")
    
    # ========== КООРДИНАТЫ (НАСТРОЙ ПОД СВОЙ ШАБЛОН) ==========
    # Левая колонка (X = 300)
    x_left = 300
    
    # Вертикальные отступы (Y)
    y_start = 300
    y_step = 40
    
    fields = {
        'vehicle_type': (x_left, y_start + 0 * y_step),
        # Категория — пропускаем
        'brand': (x_left, y_start + 2 * y_step),
        'model': (x_left, y_start + 3 * y_step),
        'year': (x_left, y_start + 4 * y_step),
        'serial': (x_left, y_start + 5 * y_step),
        'power': (x_left, y_start + 6 * y_step),
        'speed': (x_left, y_start + 7 * y_step),
        'full_name': (x_left, y_start + 9 * y_step),
        'passport': (x_left, y_start + 10 * y_step),
        'address': (x_left, y_start + 11 * y_step),
    }
    
    for field_name, (x, y) in fields.items():
        value = order_data.get(field_name, '')
        if value:
            draw.text((x, y), str(value), fill="black", font=font)
    
    # Категория — всегда СИМ
    draw.text((x_left, y_start + 1 * y_step), "СИМ", fill="black", font=font)
    
    # Серия RP, ID, № записи (в шапке)
    draw.text((300, 200), order_data.get('series_rp', ''), fill="black", font=font)
    draw.text((500, 200), order_data.get('doc_id', ''), fill="black", font=font)
    draw.text((700, 200), order_data.get('record_number', ''), fill="black", font=font)
    
    # Даты
    draw.text((300, 850), order_data.get('issue_date', ''), fill="black", font=font)
    draw.text((600, 850), order_data.get('expiry_date', ''), fill="black", font=font)
    
    # Реестровый номер, дата формирования, хеш
    draw.text((300, 1000), order_data.get('registry_number', ''), fill="black", font=font)
    draw.text((550, 1000), order_data.get('issue_date', ''), fill="black", font=font)
    draw.text((750, 1000), order_data.get('doc_hash', ''), fill="black", font=font)
    
    # Сохраняем как PDF
    output_path = f"temp_{order_data.get('id', 'unknown')}.pdf"
    img.save(output_path, "PDF", resolution=300.0)
    print(f"PDF сохранён: {output_path}")
    return output_path
