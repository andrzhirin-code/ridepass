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
    
    # Загружаем шрифт
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Координаты полей (подбери под свой шаблон)
    fields = {
        'vehicle_type': (150, 350),
        'brand': (150, 420),
        'model': (150, 490),
        'year': (150, 560),
        'power': (150, 630),
        'serial': (150, 700),
        'full_name': (150, 800),
        'passport': (150, 870),
        'address': (150, 940),
        'speed': (150, 1010),
        'issue_date': (150, 1120),
        'expiry_date': (400, 1120),
        'registry_number': (150, 1220),
        'doc_hash': (400, 1220),
    }
    
    for field_name, (x, y) in fields.items():
        value = order_data.get(field_name, '')
        if value:
            draw.text((x, y), str(value), fill="black", font=font)
    
    output_path = f"temp_{order_data.get('id', 'unknown')}.pdf"
    img.save(output_path, "PDF", resolution=100.0)
    return output_path
