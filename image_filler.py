from PIL import Image, ImageDraw, ImageFont
import os

def generate_pdf(order_data):
    template_path = "template.png"
    
    # Если нет шаблона — создаём простой PDF через fpdf2
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
    
    # Загружаем шрифт с поддержкой кириллицы
    try:
        font = ImageFont.truetype("arial.ttf", 55)
    except:
        font = ImageFont.load_default()
    
    # ========== КООРДИНАТЫ (РАССЧИТАНЫ ПО ТВОИМ ЗАМЕРАМ) ==========
    x = 980          # левая колонка
    y_start = 1086   # первое поле
    y_step = 195     # шаг между полями
    
    # Цвет текста — чёрный (фон белый)
    text_color = (0, 0, 0)
    
    # ========== ШАПКА (Серия RP, ID, № записи) ==========
    draw.text((500, 350), order_data.get('series_rp', ''), fill=text_color, font=font, anchor="ls")
    draw.text((900, 350), order_data.get('doc_id', ''), fill=text_color, font=font, anchor="ls")
    draw.text((1300, 350), order_data.get('record_number', ''), fill=text_color, font=font, anchor="ls")
    
    # ========== I. ОСНОВНЫЕ ДАННЫЕ ==========
    draw.text((x, y_start), order_data.get('vehicle_type', ''), fill=text_color, font=font, anchor="ls")
    draw.text((x, y_start + y_step), "СИМ", fill=text_color, font=font, anchor="ls")
    draw.text((x, y_start + y_step * 2), order_data.get('brand', ''), fill=text_color, font=font, anchor="ls")
    draw.text((x, y_start + y_step * 3), order_data.get('model', ''), fill=text_color, font=font, anchor="ls")
    draw.text((x, y_start + y_step * 4), order_data.get('year', ''), fill=text_color, font=font, anchor="ls")
    draw.text((x, y_start + y_step * 5), order_data.get('serial', ''), fill=text_color, font=font, anchor="ls")
    draw.text((x, y_start + y_step * 6), f"{order_data.get('power', '')} Вт", fill=text_color, font=font, anchor="ls")
    draw.text((x, y_start + y_step * 7), f"{order_data.get('speed', '')} км/ч", fill=text_color, font=font, anchor="ls")
    
    # ========== II. ДАННЫЕ О ВЛАДЕЛЬЦЕ ==========
    y_owner = y_start + y_step * 10
    draw.text((x, y_owner), order_data.get('full_name', ''), fill=text_color, font=font, anchor="ls")
    draw.text((x, y_owner + y_step), order_data.get('passport', ''), fill=text_color, font=font, anchor="ls")
    draw.text((x, y_owner + y_step * 2), order_data.get('address', ''), fill=text_color, font=font, anchor="ls")
    
    # ========== III. СРОК ДЕЙСТВИЯ ==========
    y_dates = y_start + y_step * 15
    draw.text((x, y_dates), order_data.get('issue_date', ''), fill=text_color, font=font, anchor="ls")
    draw.text((x + 400, y_dates), order_data.get('expiry_date', ''), fill=text_color, font=font, anchor="ls")
    
    # ========== V. СВЕДЕНИЯ О ДОКУМЕНТЕ ==========
    y_reg = y_start + y_step * 19
    draw.text((x, y_reg), order_data.get('registry_number', ''), fill=text_color, font=font, anchor="ls")
    draw.text((x + 400, y_reg), order_data.get('issue_date', ''), fill=text_color, font=font, anchor="ls")
    draw.text((x + 800, y_reg), order_data.get('doc_hash', ''), fill=text_color, font=font, anchor="ls")
    
    # Сохраняем PDF
    output_path = f"temp_{order_data.get('id', 'unknown')}.pdf"
    img.save(output_path, "PDF", resolution=300)
    return output_path
