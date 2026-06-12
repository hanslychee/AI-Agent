"""Render a candidate's final recruitment report as a PDF (reportlab)."""
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from ..ai.prompts import HUMAN_REVIEW_REMINDER

ACCENT = colors.HexColor("#1d4ed8")
MUTED = colors.HexColor("#64748b")


def build_report_pdf(candidate, job, analysis, evaluation, report) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm,
        title=f"Recruitment Report - {candidate.name}",
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Title"], fontSize=18, textColor=ACCENT, spaceAfter=4)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12, textColor=ACCENT, spaceBefore=10, spaceAfter=4)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=10, leading=14)
    muted = ParagraphStyle("muted", parent=body, textColor=MUTED, fontSize=9)

    content = report.content or {}
    elements = [
        Paragraph("Final Candidate Evaluation Report", h1),
        Paragraph(f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC", muted),
        Spacer(1, 6),
    ]

    rows = [
        ["Candidate", candidate.name],
        ["Job Title", job.title],
        ["CV Match Score", f"{analysis.total_score}/100 ({analysis.recommendation})" if analysis else "Not analyzed"],
        ["Interview Score", f"{evaluation.score}/100" if evaluation else "Not interviewed"],
        ["Hiring Recommendation", report.recommendation or content.get("recommendation", "")],
        ["Suggested Salary Range", report.salary_range or content.get("suggested_salary_range", "") or "—"],
        ["Status", candidate.status],
    ]
    table = Table(rows, colWidths=[55 * mm, 110 * mm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), ACCENT),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    elements.append(table)

    def section(title: str, items):
        if not items:
            return
        elements.append(Paragraph(title, h2))
        if isinstance(items, str):
            elements.append(Paragraph(items, body))
        else:
            for item in items:
                elements.append(Paragraph(f"• {item}", body))

    section("Executive Summary", content.get("executive_summary", ""))
    section("Strengths", content.get("strengths", []))
    section("Weaknesses", content.get("weaknesses", []))
    section("Concerns", content.get("concerns", []))
    if evaluation and evaluation.ai_summary:
        section("Interview Evaluation Summary", evaluation.ai_summary)
    if report.hr_notes:
        section("Final HR Notes", report.hr_notes)

    elements.append(Spacer(1, 14))
    elements.append(Paragraph(f"<b>Important:</b> {HUMAN_REVIEW_REMINDER}", muted))

    doc.build(elements)
    return buffer.getvalue()
