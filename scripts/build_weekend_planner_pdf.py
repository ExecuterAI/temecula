#!/usr/bin/env python3
"""Temecula Wine Day Planner PDF — cover logo v1; headers logo v2. Day 1/Day 2 (any weekday)."""
from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image as RLImage,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
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
RULE = HexColor("#e7e5e4")

styles = getSampleStyleSheet()
for name, kw in {
    "CoverTitle": dict(fontName="Times-Bold", fontSize=24, leading=28, textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=6),
    "CoverSub": dict(fontName="Helvetica", fontSize=11, leading=15, textColor=MUTED, alignment=TA_CENTER, spaceAfter=5),
    "H": dict(fontName="Times-Bold", fontSize=12.5, leading=16, textColor=PRIMARY, spaceBefore=9, spaceAfter=4),
    "H2": dict(fontName="Times-Bold", fontSize=11, leading=14, textColor=PRIMARY, spaceBefore=7, spaceAfter=3),
    "Body": dict(fontName="Helvetica", fontSize=9.5, leading=13, textColor=STONE, spaceAfter=5, alignment=TA_LEFT),
    "PlanBullet": dict(fontName="Helvetica", fontSize=9.5, leading=12.5, textColor=STONE),
    "Small": dict(fontName="Helvetica", fontSize=8, leading=10.5, textColor=MUTED, alignment=TA_CENTER),
    "Check": dict(fontName="Helvetica", fontSize=9.5, leading=13, textColor=STONE, leftIndent=4),
    "Cell": dict(fontName="Helvetica", fontSize=8.5, leading=11, textColor=STONE),
    "CellB": dict(fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=PRIMARY),
}.items():
    styles.add(ParagraphStyle(name=name, **kw))


def bullets(items: list[str], size: float | None = None) -> ListFlowable:
    st = styles["PlanBullet"]
    return ListFlowable(
        [ListItem(Paragraph(i, st), leftIndent=8, bulletColor=GOLD) for i in items],
        bulletType="bullet",
        start="•",
        leftIndent=10,
        spaceBefore=1,
        spaceAfter=2,
    )


def p(text: str, style: str = "Body") -> Paragraph:
    return Paragraph(text, styles[style])


def draw_cover(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(CREAM)
    canvas.rect(0, 0, letter[0], letter[1], fill=1, stroke=0)
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(1)
    canvas.rect(0.4 * inch, 0.4 * inch, letter[0] - 0.8 * inch, letter[1] - 0.8 * inch, fill=0, stroke=1)
    canvas.restoreState()


def draw_inner(canvas, doc) -> None:
    canvas.saveState()
    if LOGO_HEADER.exists():
        hw = 2.25 * inch
        hh = hw * (200 / 487)
        x = (letter[0] - hw) / 2
        y = letter[1] - 0.38 * inch - hh
        canvas.drawImage(str(LOGO_HEADER), x, y, width=hw, height=hh, mask="auto", preserveAspectRatio=True, anchor="c")
    rule_y = letter[1] - 1.38 * inch
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.55)
    canvas.line(0.7 * inch, rule_y, letter[0] - 0.7 * inch, rule_y)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawCentredString(letter[0] / 2, 0.4 * inch, f"bellieacreswine.com  ·  Temecula Wine Day Planner  ·  {doc.page - 1}")
    canvas.setStrokeColor(RULE)
    canvas.line(0.7 * inch, 0.52 * inch, letter[0] - 0.7 * inch, 0.52 * inch)
    canvas.restoreState()


def route_table(rows: list[tuple[str, str, str]]) -> Table:
    data = [[Paragraph("<b>Stop</b>", styles["CellB"]), Paragraph("<b>Estate (examples)</b>", styles["CellB"]), Paragraph("<b>Why it fits</b>", styles["CellB"])]]
    for a, b, c in rows:
        data.append([Paragraph(a, styles["CellB"]), Paragraph(b, styles["Cell"]), Paragraph(c, styles["Cell"])])
    t = Table(data, colWidths=[0.85 * inch, 2.55 * inch, 3.5 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#f5f0e8")),
                ("GRID", (0, 0), (-1, -1), 0.4, RULE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def build() -> None:
    doc = BaseDocTemplate(str(OUT), pagesize=letter, title="Temecula Wine Day Planner", author="Bellie Acres Wine")
    cover_frame = Frame(0.65 * inch, 0.65 * inch, letter[0] - 1.3 * inch, letter[1] - 1.3 * inch, id="cover")
    inner_frame = Frame(0.7 * inch, 0.65 * inch, letter[0] - 1.4 * inch, letter[1] - 0.65 * inch - 1.5 * inch, id="inner")
    doc.addPageTemplates(
        [
            PageTemplate(id="cover", frames=cover_frame, onPage=draw_cover),
            PageTemplate(id="inner", frames=inner_frame, onPage=draw_inner),
        ]
    )

    story: list = []

    # COVER — logo smaller + top pad so crown never clips on frame
    story.append(Spacer(1, 0.28 * inch))
    if LOGO_COVER.exists():
        from PIL import Image as PILImage

        iw, ih = PILImage.open(LOGO_COVER).size
        cw = 2.95 * inch  # keep well inside gold frame
        ch = cw * (ih / float(iw))
        story.append(RLImage(str(LOGO_COVER), width=cw, height=ch, hAlign="CENTER"))
    story.append(Spacer(1, 0.18 * inch))
    story.append(p("Temecula Wine<br/>Day Planner", "CoverTitle"))
    story.append(p("Printable routes · Day 1 &amp; Day 2 · Any day of the week", "CoverSub"))
    story.append(HRFlowable(width="42%", thickness=1, color=GOLD, spaceBefore=4, spaceAfter=10, hAlign="CENTER"))
    story.append(
        p(
            "Clear tasting-room clusters, timing, and sip-and-spit pacing — built for Temecula Valley visitors who want a solid plan and room to enjoy the glass.",
            "CoverSub",
        )
    )
    story.append(Spacer(1, 0.28 * inch))
    story.append(
        p(
            "Independent travel guide from bellieacreswine.com<br/>"
            "We do not sell wine or take reservations. Confirm hours, fees, and policies on each estate’s official site.<br/>"
            "21+ for alcohol. Designate a driver or use rideshare. Drink responsibly.",
            "Small",
        )
    )
    story.append(NextPageTemplate("inner"))
    story.append(PageBreak())

    # PAGE 1 content
    story.append(p("How to use this planner", "H"))
    story.append(
        p(
            "Use <b>Day 1</b> as your main tasting day (weekday or weekend). Add <b>Day 2</b> if you have a second day in the valley. "
            "Each route is a <b>cluster</b> — estates on the same corridor so you spend time tasting, not crossing the whole map. "
            "Swap any named estate using the live directory and map at <b>bellieacreswine.com</b>."
        )
    )

    story.append(p("Tasting well (sip, spit, pace)", "H"))
    story.append(
        bullets(
            [
                "<b>Sip and spit is welcome</b> at most serious tasting bars — you can evaluate more wines clearly and still drive later if you stay disciplined.",
                "Ask for a <b>dump bucket</b> and water. Spitting is normal; it is how pros taste through a long flight.",
                "A full swallow on every pour adds up fast. Keep the wines you love for a purchased bottle or a single glass with food.",
                "<b>How many stops:</b> 3 focused tastings is a classic day. With sip-and-spit, short drives, and food, <b>4 stops</b> can work beautifully when each visit stays intentional.",
                "Eat a real meal before the first pour. Alternate water. Book seated experiences when the estate requires them.",
                "Confirm morning-of policies (kids, pets, reservations) on the winery site so the day stays smooth.",
            ]
        )
    )

    story.append(p("Day 1 — Main corridor cluster (Rancho California Road spine)", "H"))
    story.append(
        p(
            "Best first day for most visitors: dense tasting rooms, food options nearby, easy swaps. "
            "Works any day of the week; weekends are busier — reserve when you can."
        )
    )
    story.append(
        route_table(
            [
                (
                    "1 · Open",
                    "Ponte Winery · or Callaway",
                    "Park-like grounds, approachable start, Rhône-leaning reds and aromatic whites. ~60–90 min.",
                ),
                (
                    "2 · Contrast",
                    "Thornton Winery · or Wilson Creek",
                    "Sparkling/celebration energy (Thornton) or lively patio social pour (Wilson Creek). Keep the drive short.",
                ),
                (
                    "Lunch",
                    "Estate restaurant or nearby sit-down",
                    "Real food resets the palate. Hydrate so the afternoon stays sharp.",
                ),
                (
                    "3 · Close",
                    "Miramonte · Falkner · or Europa Village",
                    "View deck, hillside Rhône posture, or multi-mood campus — pick one mood and finish strong.",
                ),
                (
                    "Optional 4",
                    "When the group still feels fresh",
                    "Add one short outdoor stop on the same spine with sip-and-spit pacing.",
                ),
            ]
        )
    )
    story.append(Spacer(1, 0.08 * inch))
    story.append(p("Day 1 suggested clock (adjust to your reservations)", "H2"))
    story.append(
        bullets(
            [
                "<b>10:30</b> — Arrive valley, water/coffee, confirm first reservation.",
                "<b>11:00–12:15</b> — Stop 1.",
                "<b>12:30–1:45</b> — Lunch.",
                "<b>2:15–3:30</b> — Stop 2 (or reverse Stop 2/3 if bookings require).",
                "<b>3:45–5:00</b> — Stop 3.",
                "<b>Optional</b> — Stop 4 only with sip-and-spit discipline and a sober driver plan.",
                "<b>Evening</b> — Old Town Temecula or wine-country dinner; leave room for sleep if Day 2 follows.",
            ]
        )
    )

    story.append(PageBreak())

    # PAGE 2
    story.append(p("Day 2 — Quieter corridors (De Portola · Calle Contento · side roads)", "H"))
    story.append(
        p(
            "Second day rewards a slower map: east-valley and side-road estates often feel more spacious. "
            "Ideal after a busy Day 1, or as a calmer single-day plan if you already know the main road."
        )
    )
    story.append(
        route_table(
            [
                (
                    "1 · Morning",
                    "Danza del Sol · De Portola corridor",
                    "Spanish-leaning bottles, patio pacing, softer start than the main spine.",
                ),
                (
                    "2 · Midday",
                    "Falkner Winery · hillside pair",
                    "Hilltop posture and views — strong “last good look at the valley” stop if this is your finale.",
                ),
                (
                    "Lunch",
                    "Light sit-down or picnic rules permitting",
                    "Keep alcohol modest; Day 2 is for clarity and scenery as much as pours.",
                ),
                (
                    "3 · Afternoon",
                    "Calle Contento / side-road estate of choice",
                    "Use bellieacreswine.com/map to pick a neighbor pin — stay clustered.",
                ),
            ]
        )
    )
    story.append(Spacer(1, 0.06 * inch))
    story.append(p("Day 2 suggested clock", "H2"))
    story.append(
        bullets(
            [
                "<b>10:30–12:00</b> — Stop 1.",
                "<b>12:15–1:30</b> — Lunch / rest.",
                "<b>1:45–3:15</b> — Stop 2 (views).",
                "<b>3:30–4:30</b> — Optional Stop 3, then exit while you still feel sharp.",
            ]
        )
    )

    story.append(p("Three ready-to-run day themes", "H"))
    story.append(
        bullets(
            [
                "<b>First visit:</b> Day 1 spine only — Ponte (or Callaway) → lunch → Thornton or Wilson Creek → one view/close stop. Directory: /guides/first-timer-tasting-route",
                "<b>Views &amp; photos:</b> Build around Miramonte, Falkner, and other “sip with a view” pins — /guides/sip-with-a-view — shorter pours, longer lookouts.",
                "<b>Kids or dogs:</b> Outdoor-forward estates only; confirm kid and pet notes the morning you go. Filter the directory; read /guides/pet-friendly-wineries. Prefer earlier hours and shorter flights.",
            ]
        )
    )

    story.append(p("What to ask at the bar (so every stop teaches you something)", "H"))
    story.append(
        bullets(
            [
                "What is the house style for your bestselling red versus your crispest white?",
                "Is there a reserve, library, or sparkling flight that needs a separate booking?",
                "Which bottle would you pour for someone who likes bold Temecula reds but wants one elegant option?",
                "Where should we go next on this corridor if we want quieter patio space?",
            ]
        )
    )

    story.append(p("Buying bottles without overload", "H"))
    story.append(
        p(
            "Taste with notes (phone is fine). Buy the bottles you would reorder tomorrow — not every pleasant sip. "
            "Shipping and club deals vary; ask before you load the trunk. Your future self prefers two great bottles over six maybes."
        )
    )

    story.append(PageBreak())

    # PAGE 3
    story.append(p("Corridor cheat sheet", "H"))
    story.append(
        route_table(
            [
                (
                    "Rancho California Rd",
                    "Ponte, Thornton, Callaway, Wilson Creek, South Coast, Europa…",
                    "Highest density. Best Day 1. Build buffers for parking on busy days.",
                ),
                (
                    "De Portola Rd",
                    "Danza del Sol and neighbors",
                    "Strong Day 2 / quieter-day energy.",
                ),
                (
                    "Hillside / view",
                    "Falkner and view-tagged estates",
                    "Scenery-forward finales; check /guides/sip-with-a-view.",
                ),
                (
                    "Resort-scale",
                    "South Coast, Europa Village",
                    "Food + linger time when you want one campus to do more of the work.",
                ),
            ]
        )
    )

    story.append(p("Field checklist", "H"))
    for line in [
        "☐ Sober driver or rideshare plan confirmed",
        "☐ Reservations screenshots for seated tastings",
        "☐ Water + light snacks in the car",
        "☐ Layers (patios shift with wind and evening cool)",
        "☐ Sunscreen / hat on warm afternoons",
        "☐ Dump-bucket / spit comfort — taste more, absorb less",
        "☐ Note app for “buy this bottle” vs “nice but pass”",
        "☐ bellieacreswine.com/map bookmarked for live swaps",
        "☐ Official winery sites checked for today’s hours and fees",
    ]:
        story.append(Paragraph(line, styles["Check"]))

    story.append(Spacer(1, 0.12 * inch))
    story.append(p("Keep exploring (free on the site)", "H2"))
    story.append(
        bullets(
            [
                "Full directory — bellieacreswine.com/wineries",
                "Interactive map — bellieacreswine.com/map",
                "Long-read weekend article — /guides/weekend-in-temecula-wine-country",
                "Weekday vs weekend pacing — /guides/weekday-vs-weekend-tasting",
                "Best-of shortlist — /guides/best-temecula-wineries",
            ]
        )
    )

    story.append(Spacer(1, 0.15 * inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=RULE, spaceBefore=6, spaceAfter=8))
    story.append(
        p(
            "Thank you for supporting Bellie Acres Wine — an independent Temecula wine directory.<br/>"
            "Questions: executerceo@gmail.com · Not affiliated with any single winery.<br/>"
            "Always verify details with each estate before you go. Drink responsibly.",
            "Small",
        )
    )

    doc.build(story)
    print("Wrote", OUT, "bytes", OUT.stat().st_size)


if __name__ == "__main__":
    build()
