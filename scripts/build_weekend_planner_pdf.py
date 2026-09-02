#!/usr/bin/env python3
"""Temecula Weekend Wine Planner PDF — cover = logo v1 (god bod); inner headers = logo v2 horizontal."""
from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image as RLImage,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
)

ROOT = Path("/Users/executer/bellieacreswine")
OUT = ROOT / "public/downloads/temecula-weekend-planner.pdf"
LOGO_COVER = ROOT / "public/images/brand/logo-cover-godbod.png"
LOGO_HEADER = ROOT / "public/images/brand/logo-header-horizontal.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

PRIMARY = HexColor("#5c1a1a")
GOLD = HexColor("#b08d3c")
STONE = HexColor("#44403c")
MUTED = HexColor("#78716c")
CREAM = HexColor("#faf7f2")

styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="CoverTitle",
        fontName="Times-Bold",
        fontSize=26,
        leading=32,
        textColor=PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
)
styles.add(
    ParagraphStyle(
        name="CoverSub",
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
)
styles.add(
    ParagraphStyle(
        name="PriceTag",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        textColor=GOLD,
        alignment=TA_CENTER,
        spaceAfter=10,
    )
)
styles.add(
    ParagraphStyle(
        name="H",
        fontName="Times-Bold",
        fontSize=13,
        leading=17,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="Body",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=STONE,
        spaceAfter=6,
    )
)
styles.add(
    ParagraphStyle(
        name="PlanBullet",
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=STONE,
    )
)
styles.add(
    ParagraphStyle(
        name="Small",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=MUTED,
        alignment=TA_CENTER,
    )
)
styles.add(
    ParagraphStyle(
        name="Check",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=STONE,
        leftIndent=8,
    )
)
styles.add(
    ParagraphStyle(
        name="Footer",
        fontName="Helvetica",
        fontSize=7.5,
        leading=9,
        textColor=MUTED,
        alignment=TA_CENTER,
    )
)


def bullets(items: list[str]) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(i, styles["PlanBullet"]), leftIndent=10, bulletColor=GOLD) for i in items],
        bulletType="bullet",
        start="•",
        leftIndent=12,
    )


def draw_cover(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(CREAM)
    canvas.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(1)
    canvas.rect(0.45 * inch, 0.45 * inch, letter[0] - 0.9 * inch, letter[1] - 0.9 * inch, fill=0, stroke=1)
    canvas.restoreState()


def draw_inner(canvas, doc) -> None:
    canvas.saveState()
    # Header logo #2 (horizontal) — keep compact so it stays above body
    if LOGO_HEADER.exists():
        hw = 2.35 * inch
        hh = hw * (200 / 487)
        x = (letter[0] - hw) / 2
        y = letter[1] - 0.42 * inch - hh
        canvas.drawImage(
            str(LOGO_HEADER),
            x,
            y,
            width=hw,
            height=hh,
            mask="auto",
            preserveAspectRatio=True,
            anchor="c",
        )
    rule_y = letter[1] - 1.42 * inch
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.6)
    canvas.line(0.75 * inch, rule_y, letter[0] - 0.75 * inch, rule_y)
    # Footer
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawCentredString(
        letter[0] / 2,
        0.42 * inch,
        f"bellieacreswine.com  ·  Temecula Weekend Wine Planner  ·  Page {doc.page - 1}",
    )
    canvas.setStrokeColor(HexColor("#e7e5e4"))
    canvas.line(0.75 * inch, 0.55 * inch, letter[0] - 0.75 * inch, 0.55 * inch)
    canvas.restoreState()


def build() -> None:
    doc = BaseDocTemplate(
        str(OUT),
        pagesize=letter,
        title="Temecula Weekend Wine Planner",
        author="Bellie Acres Wine",
    )

    cover_frame = Frame(
        0.7 * inch,
        0.7 * inch,
        letter[0] - 1.4 * inch,
        letter[1] - 1.4 * inch,
        id="cover",
    )
    # Top ~1.55" reserved for header logo + rule; bottom ~0.7" for footer
    inner_frame = Frame(
        0.75 * inch,
        0.7 * inch,
        letter[0] - 1.5 * inch,
        letter[1] - 0.7 * inch - 1.55 * inch,
        id="inner",
    )
    doc.addPageTemplates(
        [
            PageTemplate(id="cover", frames=cover_frame, onPage=draw_cover),
            PageTemplate(id="inner", frames=inner_frame, onPage=draw_inner),
        ]
    )

    story: list = []

    # ——— COVER (logo v1) ———
    story.append(Spacer(1, 0.15 * inch))
    if LOGO_COVER.exists():
        cover_w = 3.6 * inch
        cover_h = cover_w * (426 / 460)
        story.append(RLImage(str(LOGO_COVER), width=cover_w, height=cover_h, hAlign="CENTER"))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Temecula Weekend<br/>Wine Planner", styles["CoverTitle"]))
    story.append(Paragraph("Printable one-day &amp; two-day itineraries", styles["CoverSub"]))
    story.append(Paragraph("$2 GUIDE  ·  GOOD WINE. NO WHINE.", styles["PriceTag"]))
    story.append(HRFlowable(width="40%", thickness=1, color=GOLD, spaceBefore=2, spaceAfter=12, hAlign="CENTER"))
    story.append(
        Paragraph(
            "A simple plan so you spend the day tasting — not doom-scrolling maps in the parking lot.",
            styles["CoverSub"],
        )
    )
    story.append(Spacer(1, 0.35 * inch))
    story.append(
        Paragraph(
            "Independent travel guide only. We do not sell wine or take reservations.<br/>"
            "Confirm hours, fees, and policies on each winery’s official site.<br/>"
            "21+ for alcohol. Drink responsibly. Always keep a sober driver or rideshare plan.<br/><br/>"
            "bellieacreswine.com",
            styles["Small"],
        )
    )
    story.append(NextPageTemplate("inner"))
    story.append(PageBreak())

    # ——— PAGE 2: plan ———
    story.append(Paragraph("Before you go (5 minutes)", styles["H"]))
    story.append(
        bullets(
            [
                "Pick <b>one day</b> or <b>two days</b> below — do not mix both into one Saturday.",
                "Cap tastings at <b>2–3 per day</b>. Clusters beat checklists.",
                "Book Saturday seats the day before when you can.",
                "Eat a real meal before the first pour. Water between flights.",
                "Print this booklet or save the PDF offline on your phone.",
                "Live directory + map: <b>bellieacreswine.com/wineries</b> · <b>/map</b>",
            ]
        )
    )

    story.append(Paragraph("One perfect day (Saturday template)", styles["H"]))
    story.append(
        Paragraph(
            "<b>Idea:</b> Main-corridor morning → proper lunch → one contrast stop → done. "
            "Swap estates using the directory; keep drives short.",
            styles["Body"],
        )
    )
    story.append(
        bullets(
            [
                "<b>10:30–11:00</b> — Arrive valley; coffee/water; no heroics.",
                "<b>11:00–12:15</b> — Tasting 1 (spacious patio / easy on-ramp on or near Rancho California Rd).",
                "<b>12:30–1:45</b> — Real lunch (sit-down beats three hours of crackers).",
                "<b>2:15–3:30</b> — Tasting 2 (sparkling, view deck, or Rhône-leaning hillside — one mood).",
                "<b>Optional 4:00</b> — Light third stop only if prior drives stayed under ~10 minutes.",
                "<b>Evening</b> — Old Town or wine-country dinner; stop early enough to sleep.",
            ]
        )
    )

    story.append(Paragraph("Two-day weekend (Fri night → Sun lunch)", styles["H"]))
    story.append(Paragraph("<b>Friday</b> — Decompress, not collect stamps.", styles["Body"]))
    story.append(
        bullets(
            [
                "Check in, unpack, eat first.",
                "Optional: one nearby resort-style or patio stop only.",
                "In bed at a human hour.",
            ]
        )
    )
    story.append(Paragraph("<b>Saturday</b> — Use the One Perfect Day template above.", styles["Body"]))
    story.append(Paragraph("<b>Sunday</b> — Quieter corridors, then exit clear-headed.", styles["Body"]))
    story.append(
        bullets(
            [
                "<b>10:30</b> — East-valley / De Portola or Calle Contento–area stop (often calmer than Saturday main road).",
                "<b>12:30</b> — Optional short second outdoor stop or view moment.",
                "<b>1:30+</b> — Drive home. No “one more for the road.”",
            ]
        )
    )

    story.append(PageBreak())

    # ——— PAGE 3: vibes + checklist ———
    story.append(Paragraph("Three ready-made vibes (swap names, keep the shape)", styles["H"]))
    story.append(
        bullets(
            [
                "<b>Easy first-timers:</b> Big patio → lunch → one scenic or sparkling stop.",
                "<b>Romance / views:</b> Hillside or view deck mid-day; keep the second stop quieter; sunset photos over a fourth pour.",
                "<b>With kids or dogs:</b> Outdoor-forward estates only; shorter flights; park-and-play buffers; confirm pet/kid policies the same morning.",
            ]
        )
    )

    story.append(Paragraph("Car checklist", styles["H"]))
    for line in [
        "☐ Sober driver or rideshare plan locked",
        "☐ Water + light snacks",
        "☐ Layers (patios change with wind)",
        "☐ Reservation screenshots",
        "☐ Sunscreen / hat (summer)",
        "☐ Note app for “buy later” bottles (not everything you sipped)",
        "☐ bellieacreswine.com bookmarked for swaps",
    ]:
        story.append(Paragraph(line, styles["Check"]))

    story.append(Spacer(1, 0.25 * inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#e7e5e4"), spaceBefore=8, spaceAfter=10))
    story.append(
        Paragraph(
            "Thank you for supporting an independent Temecula wine directory.<br/>"
            "Questions: executerceo@gmail.com<br/>"
            "Not affiliated with any single winery. Drink responsibly.",
            styles["Small"],
        )
    )

    doc.build(story)
    print("Wrote", OUT, "bytes", OUT.stat().st_size, "pages≈3")


if __name__ == "__main__":
    build()
