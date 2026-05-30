from PIL import Image, ImageDraw, ImageFont
import os

def generate_pdf(order_data):
    template_path = "template.png"
    
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
    
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    # Загружаем шрифт с поддержкой русских букв
    # (если arial.ttf есть в системе — отлично, если нет — используем встроенный)
    try:
        font = ImageFont.truetype("arial.ttf", 72)
    except:
        # Пытаемся использовать другой шрифт с поддержкой кириллицы
        try:
            font = ImageFont.truetype("segoeui.ttf", 72)
        except:
            font = ImageFont.load_default()
    
    # Координаты (оставляем как есть)
    x_left = 350
    y_start = 650
    y_step = 85
    
    # Цвет текста — БЕЛЫЙ (255,255,255), чтобы было видно на тёмном фоне
    text_color = (255, 255, 255)  # белый
    
    # Шапка
    draw.text((250, 320), order_data.get('series_rp', ''), fill=text_color, font=font)
    draw.text((550, 320), order_data.get('doc_id', ''), fill=text_color, font=font)
    draw.text((850, 320), order_data.get('record_number', ''), fill=text_color, font=font)
    
    # I. ОСНОВНЫЕ ДАННЫЕ
    draw.text((x_left, y_start), order_data.get('vehicle_type', ''), fill=text_color, font=font)
    draw.text((x_left, y_start + y_step), "СИМ", fill=text_color, font=font)
    draw.text((x_left, y_start + y_step * 2), order_data.get('brand', ''), fill=text_color, font=font)
    draw.text((x_left, y_start + y_step * 3), order_data.get('model', ''), fill=text_color, font=font)
    draw.text((x_left, y_start + y_step * 4), order_data.get('year', ''), fill=text_color, font=font)
    draw.text((x_left, y_start + y_step * 5), order_data.get('serial', ''), fill=text_color, font=font)
    draw.text((x_left, y_start + y_step * 6), f"{order_data.get('power', '')} Вт", fill=text_color, font=font)
    draw.text((x_left, y_start + y_step * 7), f"{order_data.get('speed', '')} км/ч", fill=text_color, font=font)
    
    # II. ДАННЫЕ О ВЛАДЕЛЬЦЕ
    y_owner = y_start + y_step * 10
    draw.text((x_left, y_owner), order_data.get('full_name', ''), fill=text_color, font=font)
    draw.text((x_left, y_owner + y_step), order_data.get('passport', ''), fill=text_color, font=font)
    draw.text((x_left, y_owner + y_step * 2), order_data.get('address', ''), fill=text_color, font=font)
    
    # III. СРОК ДЕЙСТВИЯ
    y_dates = y_start + y_step * 15
    draw.text((x_left, y_dates), order_data.get('issue_date', ''), fill=text_color, font=font)
    draw.text((x_left + 400, y_dates), order_data.get('expiry_date', ''), fill=text_color, font=font)
    
    # V. СВЕДЕНИЯ О ДОКУМЕНТЕ
    y_reg = y_start + y_step * 19
    draw.text((x_left, y_reg), order_data.get('registry_number', ''), fill=text_color, font=font)
    draw.text((x_left + 450, y_reg), order_data.get('issue_date', ''), fill=text_color, font=font)
    draw.text((x_left + 900, y_reg), order_data.get('doc_hash', ''), fill=text_color, font=font)
    
    output_path = f"temp_{order_data.get('id', 'unknown')}.pdf"
    img.save(output_path, "PDF", resolution=300)
    return output_path
