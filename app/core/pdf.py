from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import arabic_reshaper
from bidi.algorithm import get_display

from app.core.db import Database


def _ensure_font(font_path: Path) -> str:
    name = "NotoNaskhArabic"
    try:
        pdfmetrics.getFont(name)
        return name
    except Exception:
        pass
    if font_path.exists():
        pdfmetrics.registerFont(TTFont(name, str(font_path)))
    return name


def _shape_if_ar(text: str) -> str:
    if not text:
        return ""
    # Perform Arabic shaping and bidi
    try:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


def generate_document_pdf(db: Database, doc_id: int, out_path: Path, base_dir: Path) -> None:
    font_path = base_dir / "app" / "assets" / "fonts" / "NotoNaskhArabic-Regular.ttf"
    font_name = _ensure_font(font_path)
    c = canvas.Canvas(str(out_path), pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20 * mm, height - 20 * mm, "Gestion Commerciale")

    # Fetch document data
    doc = db.query("SELECT d.*, p.name_fr as partner_name_fr, p.name_ar as partner_name_ar FROM documents d LEFT JOIN partners p ON p.id=d.partner_id WHERE d.id=?", (doc_id,))
    if not doc:
        c.drawString(20 * mm, height - 30 * mm, f"Document ID {doc_id} introuvable")
        c.save()
        return
    d = doc[0]
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, height - 30 * mm, f"{d['kind'].upper()} N? {d['number']} - {d['date']}")

    # Partner
    y = height - 40 * mm
    c.setFont(font_name, 12)
    c.drawRightString(width - 20 * mm, y, _shape_if_ar(d["partner_name_ar"]))
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, y, d["partner_name_fr"] or "")
    y -= 10 * mm

    # Lines
    c.setFont("Helvetica-Bold", 10)
    c.drawString(20 * mm, y, "D?signation")
    c.drawRightString(150 * mm, y, "Qt?")
    c.drawRightString(180 * mm, y, "PU HT")
    y -= 6 * mm
    c.setFont("Helvetica", 10)
    lines = db.query("SELECT description, qty, unit_price FROM document_lines WHERE document_id=?;", (doc_id,))
    for line in lines:
        c.drawString(20 * mm, y, line["description"])
        c.drawRightString(150 * mm, y, f"{line['qty']:.2f}")
        c.drawRightString(180 * mm, y, f"{line['unit_price']:.2f}")
        y -= 6 * mm
        if y < 30 * mm:
            c.showPage()
            y = height - 20 * mm

    # Totals
    y -= 10 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(180 * mm, y, f"Total HT: {d['total_ht']:.2f}")
    y -= 6 * mm
    c.drawRightString(180 * mm, y, f"TVA: {d['total_tva']:.2f}")
    y -= 6 * mm
    c.drawRightString(180 * mm, y, f"Total TTC: {d['total_ttc']:.2f}")

    c.showPage()
    c.save()

