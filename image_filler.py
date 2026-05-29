from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import os

def generate_pdf(order_data):
    output_path = f"temp_{order_data.get('id', 'unknown')}.pdf"
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Шапка
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "RIDEPASS")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, "ЭЛЕКТРОННАЯ РЕГИСТРАЦИЯ СИМ")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 100, "КАРТОЧКА ТРАНСПОРТНОГО СРЕДСТВА")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 120, "ПЕРСОНАЛЬНОЕ ЭЛЕКТРИЧЕСКОЕ ТРАНСПОРТНОЕ СРЕДСТВО")
    
    # Реестровая запись
    c.setFont("Helvetica", 9)
    c.drawString(50, height - 145, "Реестровая запись в системе RidePass")
    
    # Таблица с серией, ID, номером записи
    c.rect(50, height - 170, 150, 20)
    c.rect(200, height - 170, 150, 20)
    c.rect(350, height - 170, 150, 20)
    c.drawString(55, height - 163, f"Серия RP: {order_data.get('series_rp', 'RP-XXXXX')}")
    c.drawString(205, height - 163, f"ID: {order_data.get('doc_id', 'ID-XXXXX')}")
    c.drawString(355, height - 163, f"№ записи: {order_data.get('record_number', 'XXXXX')}")
    
    y = height - 220
    
    # Раздел I
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "I. ОСНОВНЫЕ ДАННЫЕ")
    y -= 20
    c.setFont("Helvetica", 10)
    fields = [
        f"1. Тип транспортного средства: {order_data.get('vehicle_type', '')}",
        f"2. Категория: СИМ",
        f"3. Марка: {order_data.get('brand', '')}",
        f"4. Модель: {order_data.get('model', '')}",
        f"5. Год выпуска: {order_data.get('year', '')}",
        f"6. Идентификационный номер: {order_data.get('serial', '')}",
        f"7. Мощность двигателя: {order_data.get('power', '')} Вт",
        f"8. Максимальная скорость: {order_data.get('speed', '')} км/ч",
    ]
    for field in fields:
        c.drawString(50, y, field)
        y -= 15
    
    y -= 10
    
    # Раздел II
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "II. ДАННЫЕ О ВЛАДЕЛЬЦЕ")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Фамилия, имя, отчество: {order_data.get('full_name', '')}")
    y -= 15
    c.drawString(50, y, f"Паспорт: {order_data.get('passport', '')}")
    y -= 15
    c.drawString(50, y, f"Адрес регистрации: {order_data.get('address', '')}")
    
    y -= 25
    
    # Раздел III
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "III. СРОК ДЕЙСТВИЯ")
    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Дата выдачи: {order_data.get('issue_date', '')}")
    c.drawString(200, y, f"Действительна до: {order_data.get('expiry_date', '')}")
    
    y -= 30
    
    # Раздел IV
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "IV. СТАТУС ТРАНСПОРТНОГО СРЕДСТВА")
    y -= 20
    c.setFont("Helvetica", 8)
    c.drawString(50, y, "НЕ ТРЕБУЕТ ПОСТАНОВКИ НА УЧЕТ В ГИБДД")
    c.drawString(210, y, "НЕ ТРЕБУЕТ ВОДИТЕЛЬСКОГО УДОСТОВЕРЕНИЯ")
    c.drawString(380, y, "ДЛЯ ЛИЧНОГО ИСПОЛЬЗОВАНИЯ")
    
    y -= 40
    
    # Раздел V
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "V. СВЕДЕНИЯ О ДОКУМЕНТЕ")
    y -= 20
    c.setFont("Helvetica", 9)
    c.drawString(50, y, f"РЕЕСТРОВЫЙ НОМЕР: {order_data.get('registry_number', '')}")
    c.drawString(220, y, f"ДАТА ФОРМИРОВАНИЯ: {order_data.get('issue_date', '')}")
    c.drawString(380, y, f"ХЕШ ДОКУМЕНТА: {order_data.get('doc_hash', '')}")
    
    # Подвал
    y = 50
    c.setFont("Helvetica", 8)
    c.drawString(50, y, "Электронная регистрация средства индивидуальной мобильности")
    c.drawString(50, y - 15, "Данный документ сформирован в электронном виде")
    c.drawString(50, y - 30, "Проверка подлинности на сайте: ridepass.ru/check")
    
    c.save()
    return output_path
