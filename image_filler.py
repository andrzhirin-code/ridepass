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
    
    # Крупный шрифт
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()
    
    width, height = img.size
    
    # Все поля в левой части, с большим отступом
    x_pos = 300
    y = 350
    y_step = 45
    
    # Основные данные
    draw.text((x_pos, y), order_data.get('vehicle_type', ''), fill="black", font=font)
    draw.text((x_pos, y + y_step), "СИМ", fill="black", font=font)
    draw.text((x_pos, y + y_step * 2), order_data.get('brand', ''), fill="black", font=font)
    draw.text((x_pos, y + y_step * 3), order_data.get('model', ''), fill="black", font=font)
    draw.text((x_pos, y + y_step * 4), order_data.get('year', ''), fill="black", font=font)
    draw.text((x_pos, y + y_step * 5), order_data.get('serial', ''), fill="black", font=font)
    draw.text((x_pos, y + y_step * 6), f"{order_data.get('power', '')} Вт", fill="black", font=font)
    draw.text((x_pos, y + y_step * 7), f"{order_data.get('speed', '')} км/ч", fill="black", font=font)
    
    # Владелец
    y_owner = y + y_step * 9
    draw.text((x_pos, y_owner), order_data.get('full_name', ''), fill="black", font=font)
    draw.text((x_pos, y_owner + y_step), order_data.get('passport', ''), fill="black", font=font)
    draw.text((x_pos, y_owner + y_step * 2), order_data.get('address', ''), fill="black", font=font)
    
    # Даты
    y_dates = y + y_step * 14
    draw.text((x_pos, y_dates), order_data.get('issue_date', ''), fill="black", font=font)
    draw.text((x_pos + 250, y_dates), order_data.get('expiry_date', ''), fill="black", font=font)
    
    # Реестр и хеш
    y_reg = y + y_step * 17
    draw.text((x_pos, y_reg), order_data.get('registry_number', ''), fill="black", font=font)
    draw.text((x_pos + 250, y_reg), order_data.get('issue_date', ''), fill="black", font=font)
    draw.text((x_pos + 500, y_reg), order_data.get('doc_hash', ''), fill="black", font=font)
    
    # Серия RP, ID, № записи (шапка)
    draw.text((250, 180), order_data.get('series_rp', ''), fill="black", font=font)
    draw.text((450, 180), order_data.get('doc_id', ''), fill="black", font=font)
    draw.text((650, 180), order_data.get('record_number', ''), fill="black", font=font)
    
    output_path = f"temp_{order_data.get('id', 'unknown')}.pdf"
    img.save(output_path, "PDF", resolution=300)
    return output_path
