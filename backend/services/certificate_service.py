"""
certificate_service.py
Generates certificate records. Optional PDF generation via reportlab if installed.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional


def generate_certificate_id() -> str:
    return f"LT-{uuid.uuid4().hex[:12].upper()}"


def build_certificate_doc(
    user_id: str,
    user_name: str,
    video_id: str,
    course_title: str,
) -> dict:
    now = datetime.now(timezone.utc)
    cert_id = generate_certificate_id()
    return {
        "certificate_id": cert_id,
        "user_id": user_id,
        "user_name": user_name,
        "video_id": video_id,
        "course_title": course_title,
        "completion_date": now.strftime("%B %d, %Y"),
        "issued_at": now.isoformat(),
    }


def generate_pdf_certificate(cert: dict) -> Optional[bytes]:
    """
    Optionally generates a PDF certificate using reportlab.
    Returns None if reportlab is not installed.
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        import io

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Background
        c.setFillColor(colors.HexColor("#f0f4ff"))
        c.rect(0, 0, width, height, fill=1, stroke=0)

        # Border
        c.setStrokeColor(colors.HexColor("#3b5bdb"))
        c.setLineWidth(6)
        c.rect(20, 20, width - 40, height - 40, fill=0, stroke=1)

        # Title
        c.setFillColor(colors.HexColor("#3b5bdb"))
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(width / 2, height - 120, "Certificate of Completion")

        # Platform
        c.setFont("Helvetica", 18)
        c.setFillColor(colors.HexColor("#555555"))
        c.drawCentredString(width / 2, height - 160, "LearnTube")

        # Body
        c.setFont("Helvetica", 14)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2, height - 230, "This is to certify that")

        c.setFont("Helvetica-Bold", 26)
        c.setFillColor(colors.HexColor("#1a1a2e"))
        c.drawCentredString(width / 2, height - 280, cert["user_name"])

        c.setFont("Helvetica", 14)
        c.setFillColor(colors.black)
        c.drawCentredString(width / 2, height - 320, "has successfully completed the course")

        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.HexColor("#3b5bdb"))
        c.drawCentredString(width / 2, height - 360, cert["course_title"])

        # Date & ID
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.HexColor("#666666"))
        c.drawCentredString(width / 2, height - 430, f"Completion Date: {cert['completion_date']}")
        c.drawCentredString(width / 2, height - 455, f"Certificate ID: {cert['certificate_id']}")

        c.save()
        buffer.seek(0)
        return buffer.read()

    except ImportError:
        return None
