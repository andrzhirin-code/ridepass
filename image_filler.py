    # 4. Рисуем текст поверх со своим шрифтом (единый блок)
    for fd in fields_data:
        fontsize = fd["fontsize"]
        rect = fd["rect"]
        value = fd["value"]

        if fd["name"] == "record_number":
            # ── Для record_number ──────────────────────────────────────
            # 1. Расширяем rect вниз в 1.5 раза для крупного шрифта
            # 2. Делаем отступ снизу 15pt, чтобы не обрезалось
            # 3. Цикл с шагом -1 для точного подбора
            expanded_rect = fitz.Rect(
                rect.x0 + 2,
                rect.y0,
                rect.x1 - 2,
                rect.y0 + rect.height * 1.5
            )
            draw_rect = fitz.Rect(
                expanded_rect.x0,
                expanded_rect.y0,
                expanded_rect.x1,
                expanded_rect.y1 - 15
            )
            rc = -1
            while fontsize > 4:
                rc = page.insert_textbox(
                    draw_rect,
                    value,
                    fontname=font_name,
                    fontfile=FONT_PATH,
                    fontsize=fontsize,
                    color=fd["color"],
                    align=fd["align"],
                )
                if rc >= 0:
                    break
                fontsize -= 1
        elif fd["name"] == "address":
            # ── Многострочное ──────────────────────────────────────────
            rc = -1
            while fontsize > 4:
                rc = page.insert_textbox(
                    fitz.Rect(rect.x0 + 2, rect.y0 + 2, rect.x1 - 2, rect.y1 - 2),
                    value,
                    fontname=font_name,
                    fontfile=FONT_PATH,
                    fontsize=fontsize,
                    color=fd["color"],
                    align=fd["align"],
                )
                if rc >= 0:
                    break
                fontsize -= 2 if fontsize > 20 else 0.5
        else:
            # ── Однострочное (центрирование через top_pad) ─────────────
            rc = -1
            while fontsize > 4:
                top_pad = (rect.height - fontsize) / 2
                if top_pad < 0:
                    top_pad = 0
                draw_rect = fitz.Rect(
                    rect.x0 + 2,
                    rect.y0 + top_pad,
                    rect.x1 - 2,
                    rect.y1,
                )
                rc = page.insert_textbox(
                    draw_rect,
                    value,
                    fontname=font_name,
                    fontfile=FONT_PATH,
                    fontsize=fontsize,
                    color=fd["color"],
                    align=fd["align"],
                )
                if rc >= 0:
                    break
                fontsize -= 2 if fontsize > 20 else 0.5

        if fontsize <= 4:
            send_telegram(f"⚠️ Не влезло: {fd['name']}")

    # 5. ВПАИВАЕМ текст ЧЕРЕЗ РАСТЕРИЗАЦИЮ (100% защита от выделения)
    # Старые wrap_contents() и clean=True не гарантируют результат
    print(f"[INFO] PyMuPDF version: {fitz.version}")
    
    # QR-код уже вставлен до этого шага, всё ок
    # Создаём растровую копию страницы с высоким качеством
    mat = fitz.Matrix(2.5, 2.5)  # DPI ~ 2.5x (достаточно для качества)
    pix = page.get_pixmap(matrix=mat)
    
    # Сохраняем как PNG в память
    img_bytes = pix.tobytes("png")

    # Создаём новый документ и вставляем картинку
    new_doc = fitz.open()
    new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
    new_page.insert_image(page.rect, stream=img_bytes)

    # Запрет на выделение и копирование (для нового документа)
    perm_mask = fitz.PDF_PERM_ACCESSIBILITY 

    output_path = os.path.join(BASE_DIR, f"order_{data.get('entry_number', 'temp')}.pdf")
    new_doc.save(
        output_path,
        garbage=4,
        deflate=True,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        owner_pw=os.urandom(16).hex(),
        permissions=perm_mask,
    )
    new_doc.close()
    doc.close()

    print(f"✅ Документ успешно сгенерирован и аппаратно заблокирован: {output_path}")
    return output_path
