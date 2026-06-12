import os
import re
import fitz
import qrcode
from io import BytesIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "template_form.pdf")
FONT_PATH = os.path.join(BASE_DIR, "timesbd.ttf")

# ── Кеш координат полей (читается один раз при старте) ──────────────────────
_FIELD_CACHE: dict | None = None


def _load_field_cache() -> dict:
    """
    Читает все поля из PDF-шаблона один раз и сохраняет координаты,
    цвет, размер шрифта и выравнивание в словарь.
    """
    global _FIELD_CACHE
    if _FIELD_CACHE is not None:
        return _FIELD_CACHE

    doc = fitz.open(TEMPLATE_PATH)
    page = doc.load_page(0)
    page_width = page.rect.width   # ~3720 у твоего шаблона

    cache = {}
    for field in page.widgets():
        name = field.field_name
        xref = field._annot.xref
        da_tuple = doc.xref_get_key(xref, "DA")
        da_str = da_tuple[1] if da_tuple and len(da_tuple) > 1 else ""

        # Размер шрифта из /DA  →  нормализуем в pt (делим на масштаб)
        scale = page_width / 595.28
        fontsize = 10.0
        m = re.search(r"([\d.]+)\s+Tf", da_str)
        if m:
            fontsize = float(m.group(1)) / scale

        # Выравнивание из /Q
        q_tuple = doc.xref_get_key(xref, "Q")
        q_val = int(q_tuple[1]) if q_tuple and q_tuple[1].isdigit() else 0
        align_map = {0: fitz.TEXT_ALIGN_LEFT,
                     1: fitz.TEXT_ALIGN_CENTER,
                     2: fitz.TEXT_ALIGN_RIGHT}
        align = align_map.get(q_val, fitz.TEXT_ALIGN_LEFT)

        # Цвет из /DA
        color = (0.054, 0.286, 0.615)   # синий по умолчанию (шапка)
        m_rgb = re.search(r"([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+rg", da_str)
        if m_rgb:
            color = (float(m_rgb.group(1)),
                     float(m_rgb.group(2)),
                     float(m_rgb.group(3)))
        else:
            m_g = re.search(r"([\d.]+)\s+g\b", da_str)
            if m_g:
                g = float(m_g.group(1))
                color = (g, g, g)
            else:
                m_k = re.search(
                    r"([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+k", da_str)
                if m_k:
                    c, mg, y, k = [float(m_k.group(i)) for i in range(1, 5)]
                    color = ((1-c)*(1-k), (1-mg)*(1-k), (1-y)*(1-k))

        cache[name] = {
            "rect":     field.rect,
            "fontsize": fontsize,
            "align":    align,
            "color":    color,
        }

    doc.close()
    _FIELD_CACHE = cache
    print(f"[CACHE] Загружено {len(cache)} полей из шаблона")
    return cache


def _draw_field(page, params: dict, value: str, font_name: str,
                is_multiline: bool = False):
    """
    Рисует текст в поле. Автоматически уменьшает шрифт если не влезает.
    """
    rect = params["rect"]
    fontsize = params["fontsize"]
    color = params["color"]
    align = params["align"]

    # Отступ пропорционален размеру страницы
    pad = 2

    if is_multiline:
        draw_rect = fitz.Rect(rect.x0 + pad, rect.y0 + pad,
                              rect.x1 - pad, rect.y1 - pad)
        rc = -1
        while fontsize > 4:
            rc = page.insert_textbox(
                draw_rect, value,
                fontname=font_name, fontfile=FONT_PATH,
                fontsize=fontsize, color=color, align=align,
            )
            if rc >= 0:
                break
            fontsize -= 1
        return rc

    else:
        # Однострочное: центрируем вертикально
        rc = -1
        while fontsize > 4:
            line_height = fontsize * 1.2
            center_y = rect.y0 + rect.height / 2
            line_rect = fitz.Rect(
                rect.x0 + pad,
                center_y - line_height / 2,
                rect.x1 - pad,
                center_y + line_height / 2,
            )
            rc = page.insert_textbox(
                line_rect, value,
                fontname=font_name, fontfile=FONT_PATH,
                fontsize=fontsize, color=color, align=align,
            )
            if rc >= 0:
                break
            fontsize -= 1
        return rc


# ── Главная функция ──────────────────────────────────────────────────────────

def fill_order_template(data: dict) -> str:
    print("📝 fill_order_template: старт")

    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Шаблон не найден: {TEMPLATE_PATH}")
    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError(
            f"Шрифт не найден: {FONT_PATH}\n"
            "Положите файл timesbd.ttf рядом с image_filler.py"
        )

    # Загружаем координаты полей (из кеша или из PDF)
    field_cache = _load_field_cache()

    # Данные для заполнения
    field_mapping = {
        "record_number":      str(data.get("passport_number", "")).replace("№", ""),
        "series":             str(data.get("series_code", "")),
        "entry_number":       str(data.get("entry_number", "")),
        "issue_date":         str(data.get("issue_date", "")),
        "vehicle_type_vision":str(data.get("vehicle_type_vision", "")),
        "brand":              str(data.get("brand", "")),
        "model":              str(data.get("model", "")),
        "year":               str(data.get("year", "")),
        "frame_number":       str(data.get("frame_number", "")),
        "engine_number":      str(data.get("engine_number", "")),
        "vehicle_type":       "Спортинвентарь",
        "engine_capacity":    str(data.get("engine_capacity", "")),
        "strokes":            str(data.get("strokes", "")),
        "cooling":            str(data.get("cooling", "")),
        "transmission":       str(data.get("transmission", "")),
        "fuel_system":        str(data.get("fuel_system", "")),
        "front_brake":        str(data.get("front_brake", "")),
        "rear_brake":         str(data.get("rear_brake", "")),
        "weight":             str(data.get("weight", "")),
        "full_name":          str(data.get("full_name", "")),
        "passport":           str(data.get("passport", "")),
        "address":            str(data.get("address", "")),
        "doc_hash":           str(data.get("doc_hash", "")),
    }

    # Многострочные поля
    multiline_fields = {"address"}

    doc = fitz.open(TEMPLATE_PATH)
    page = doc.load_page(0)

    # 1. Регистрируем шрифт
    font_name = "TimesNewRomanBold"
    page.insert_font(fontname=font_name, fontfile=FONT_PATH)

    # 2. Удаляем интерактивные поля
    widgets_to_delete = list(page.widgets())
    for w in widgets_to_delete:
        page.delete_widget(w)

    # 3. Рисуем текст напрямую
    for field_name, value in field_mapping.items():
        if not value:
            continue
        if field_name not in field_cache:
            print(f"⚠️ Поле '{field_name}' не найдено в шаблоне — пропускаем")
            continue

        params = dict(field_cache[field_name])  # копия чтобы не менять кеш

        # record_number — ограничиваем максимальный размер высотой поля
        if field_name == "record_number":
            rect = params["rect"]
            max_fs = rect.height * 0.75 / (page.rect.width / 595.28)
            # max_fs уже в нормализованных pt, params["fontsize"] тоже
            # rect.height в единицах PDF, нормализуем
            scale = page.rect.width / 595.28
            max_fs_pt = (rect.height * 0.75) / scale
            params["fontsize"] = min(params["fontsize"], max_fs_pt)

        is_multi = field_name in multiline_fields
        rc = _draw_field(page, params, value, font_name, is_multi)

        if rc is not None and rc < 0:
            print(f"⚠️ Не влезло: {field_name}")

    # 4. Впаиваем текст в страницу
    page.wrap_contents()

    # 5. QR-код
    page_width = float(page.rect.x1)
    page_height = float(page.rect.y1)
    qr_size = page_width * 0.054      # ~200 единиц при ширине 3720
    qr_x = page_width - qr_size * 1.3
    qr_y = page_height * 0.13
    qr_rect = fitz.Rect(qr_x, qr_y, qr_x + qr_size, qr_y + qr_size)

    verification_url = (
        f"https://ridepass.onrender.com/check?code={data.get('entry_number', '')}"
    )
    qr = qrcode.QRCode(box_size=15, border=1)
    qr.add_data(verification_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_bytes = BytesIO()
    qr_img.save(qr_bytes, "PNG")
    qr_bytes.seek(0)
    page.insert_image(qr_rect, stream=qr_bytes)

    # 6. Сохраняем с защитой
    perm_mask = fitz.PDF_PERM_ACCESSIBILITY
    output_path = os.path.join(
        BASE_DIR, f"order_{data.get('entry_number', 'temp')}.pdf"
    )
    doc.save(
        output_path,
        garbage=4,
        deflate=True,
        clean=True,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        owner_pw=os.urandom(16).hex(),
        permissions=perm_mask,
    )
    doc.close()

    print(f"✅ Готово: {output_path}")
    return output_path
