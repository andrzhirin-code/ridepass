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
    
    font = ImageFont.load_default()
    
    # ТЕСТ: рисуем текст в конкретных местах
    draw.text((300, 600), "ТЕСТ ТИП ТС (300,600)", fill="black", font=font)
    draw.text((300, 700), "ТЕСТ МАРКА (300,700)", fill="black", font=font)
    draw.text((300, 800), "ТЕСТ МОДЕЛЬ (300,800)", fill="black", font=font)
    draw.text((300, 900), "ТЕСТ ФИО (300,900)", fill="black", font=font)
    
    output_path = f"temp_{order_data.get('id', 'unknown')}.pdf"
    img.save(output_path, "PDF", resolution=300)
    return output_path
