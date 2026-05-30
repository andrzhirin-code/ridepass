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
    
    # Загружаем стандартный шрифт (он поддерживает кириллицу в последних версиях PIL)
    # Увеличиваем размер через масштабирование
    try:
        font = ImageFont.truetype("arial.ttf", 72)
    except:
        # Если arial.ttf нет, используем дефолтный, но его размер фиксирован
        font = ImageFont.load_default()
    
    # Цвет текста — чёрный (фон белый)
    text_color = (0, 0, 0)
    
    # КООРДИНАТЫ ДЛЯ A4 (2480×3508 px)
    # Основано на структуре твоего шаблона
    x = 300      # отступ слева
    y_start = 600
    step = 85    # шаг между строками
    
    # Шапка (Серия RP, ID, № записи)
    draw.text((300, 350), order_data.get('series_rp', ''), fill=text_color, font=font)
    draw.text((600, 350), order_data.get('doc_id', ''), fill=text_color, font=font)
    draw.text((900, 350), order_data.get('record_number', ''), fill=text_color, font=font)
    
    # I. ОСНОВНЫЕ ДАННЫЕ
    draw.text((x, y_start), order_data.get('vehicle_type', ''), fill=text_color, font=font)
    draw.text((x, y_start + step), "СИМ", fill=text_color, font=font)
    draw.text((x, y_start + step * 2), order_data.get('brand', ''), fill=text_color, font=font)
    draw.text((x, y_start + step * 3), order_data.get('model', ''), fill=text_color, font=font)
    draw.text((x, y_start + step * 4), order_data.get('year', ''), fill=text_color, font=font)
    draw.text((x, y_start + step * 5), order_data.get('serial', ''), fill=text_color, font=font)
    draw.text((x, y_start + step * 6), f"{order_data.get('power', '')} Вт", fill=text_color, font=font)
    draw.text((x, y_start + step * 7), f"{order_data.get('speed', '')} км/ч", fill=text_color, font=font)
    
    # II. ДАННЫЕ О ВЛАДЕЛЬЦЕ
    y_owner = y_start + step * 10
    draw.text((x, y_owner), order_data.get('full_name', ''), fill=text_color, font=font)
    draw.text((x, y_owner + step), order_data.get('passport', ''), fill=text_color, font=font)
    draw.text((x, y_owner + step * 2), order_data.get('address', ''), fill=text_color, font=font)
    
    # III. СРОК ДЕЙСТВИЯ
    y_dates = y_start + step * 15
    draw.text((x, y_dates), order_data.get('issue_date', ''), fill=text_color, font=font)
    draw.text((x + 300, y_dates), order_data.get('expiry_date', ''), fill=text_color, font=font)
    
    # V. СВЕДЕНИЯ О ДОКУМЕНТЕ
    y_reg = y_start + step * 19
    draw.text((x, y_reg), order_data.get('registry_number', ''), fill=text_color, font=font)
    draw.text((x + 350, y_reg), order_data.get('issue_date', ''), fill=text_color, font=font)
    draw.text((x + 700, y_reg), order_data.get('doc_hash', ''), fill=text_color, font=font)
    
    output_path = f"temp_{order_data.get('id', 'unknown')}.pdf"
    img.save(output_path, "PDF", resolution=300)
    return output_path
