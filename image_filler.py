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
    
    # Загружаем шрифт
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    width, height = img.size
    print(f"Размер шаблона: {width}x{height}")
    
    # ========== РИСУЕМ СЕТКУ ==========
    # Красные линии каждые 100 пикселей
    for x in range(0, width, 100):
        draw.line((x, 0, x, height), fill="red", width=2)
    for y in range(0, height, 100):
        draw.line((0, y, width, y), fill="red", width=2)
    
    # Синие координаты
    for x in range(0, width, 100):
        for y in range(0, height, 100):
            draw.text((x + 5, y + 5), f"{x},{y}", fill="blue", font=font)
    
    # ========== ВРЕМЕННЫЕ ДАННЫЕ ДЛЯ ТЕСТА ==========
    # (чтобы видеть, куда попадает текст)
    draw.text((100, 100), "ТЕСТОВЫЙ ТЕКСТ (100,100)", fill="black", font=font)
    draw.text((300, 500), "ТЕСТ (300,500)", fill="black", font=font)
    draw.text((500, 800), "ТЕСТ (500,800)", fill="black", font=font)
    
    output_path = f"temp_{order_data.get('id', 'unknown')}.pdf"
    img.save(output_path, "PDF", resolution=300)
    print(f"PDF с сеткой сохранён: {output_path}")
    return output_path
