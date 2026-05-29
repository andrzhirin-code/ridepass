from PIL import Image, ImageDraw, ImageFont
import os

def fill_template(order_data, output_path):
    template_path = "template.png"
    if not os.path.exists(template_path):
        raise FileNotFoundError("template.png not found")
    
    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Позиции для текста (подбери под свою картинку)
    positions = {
        "vehicle_type": (200, 350),
        "brand": (200, 400),
        "model": (200, 450),
        "year": (200, 500),
        "power": (200, 550),
        "serial": (200, 600),
        "full_name": (200, 700),
        "passport": (200, 750),
        "address": (200, 800),
        "speed": (200, 650),
    }
    
    for key, pos in positions.items():
        if key in order_data and order_data[key]:
            draw.text(pos, str(order_data[key]), fill="black", font=font)
    
    img.save(output_path, "PDF", resolution=100.0)

def generate_pdf(order_data):
    output_path = f"temp_{order_data.get('id', 'unknown')}.pdf"
    fill_template(order_data, output_path)
    return output_path
