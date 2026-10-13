#!/usr/bin/env python3
"""One-page De Portola Wine Trail map. Title on top. Horizontal logo + website in the footer."""
from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path("/Users/executer/bellieacreswine")
OUT = ROOT / "public/downloads/de-portola-wine-trail-map.pdf"
LOGO = ROOT / "public/images/brand/logo-header-horizontal.png"

SAGE = HexColor("#4A5E4E")
INK = HexColor("#2B322C")
CREAM = HexColor("#F6F7F2")
STONE = HexColor("#5c665e")
LINE = HexColor("#d7ddd4")

# Official trail order, south to north. Coordinates already on the published cards.
STOPS = [
    (1, "Somerset", "37338 De Portola Rd", 33.509267, -117.017936),
    (2, "Fazeli Cellars", "37320 De Portola Rd", 33.509110265718, -117.018027600553),
    (3, "Robert Renzoni", "37350 De Portola Rd", 33.509375342055, -117.01786861906),
    (4, "Altísima", "37440 De Portola Rd", 33.510207418639, -117.01747767541),
    (5, "Gershon Bachus", "37750 De Portola Rd", 33.5166822, -117.0156341),
    (6, "Oak Mountain", "36522 Via Verde", 33.517534, -117.021015),
    (7, "Leoness", "38311 De Portola Rd", 33.523172756599, -117.019242238273),
    (8, "Danza del Sol", "39050 De Portola Rd", 33.533618, -117.013656),
    (9, "Frangipani", "39750 De Portola Rd", 33.540753, -117.007797),
    (10, "Cougar", "39870 De Portola Rd", 33.54215548238, -117.006361672645),
    (11, "Masia de la Vinya", "40230 De Portola Rd", 33.544692217025, -117.003939978343),
]


def project(lat, lng, box):
    x0, y0, x1, y1 = box
    lats = [s[3] for s in STOPS]
    lngs = [s[4] for s in STOPS]
    pad_lat = (max(lats) - min(lats)) * 0.12
    pad_lng = (max(lngs) - min(lngs)) * 0.16
    min_lat, max_lat = min(lats) - pad_lat, max(lats) + pad_lat
    min_lng, max_lng = min(lngs) - pad_lng, max(lngs) + pad_lng
    x = x0 + (lng - min_lng) / (max_lng - min_lng) * (x1 - x0)
    y = y0 + (lat - min_lat) / (max_lat - min_lat) * (y1 - y0)
    return x, y


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    width, height = letter[1], letter[0]  # landscape
    c = canvas.Canvas(str(OUT), pagesize=(width, height))
    c.setTitle("De Portola Wine Trail")
    c.setAuthor("Bellie Acres Wine")

    c.setFillColor(CREAM)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    c.setFillColor(SAGE)
    c.rect(0, height - 78, width, 78, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Times-Bold", 28)
    c.drawString(36, height - 42, "De Portola Wine Trail")
    c.setFont("Times-Italic", 12)
    c.drawString(36, height - 62, "Eleven wineries · Temecula Valley · south of Rancho California Road")

    map_box = (36, 78, 430, height - 100)
    c.setFillColor(white)
    c.setStrokeColor(LINE)
    c.setLineWidth(1)
    c.roundRect(map_box[0], map_box[1], map_box[2] - map_box[0], map_box[3] - map_box[1], 10, fill=1, stroke=1)

    # A light country-road hint, not a surveyed centerline.
    road = [project(s[3], s[4], map_box) for s in STOPS]
    c.setStrokeColor(HexColor("#c5d0c2"))
    c.setLineWidth(3)
    c.setLineCap(1)
    path = c.beginPath()
    path.moveTo(road[0][0], road[0][1])
    for x, y in road[1:]:
        path.lineTo(x, y)
    c.drawPath(path, stroke=1, fill=0)

    for num, name, _addr, lat, lng in STOPS:
        x, y = project(lat, lng, map_box)
        c.setFillColor(SAGE)
        c.circle(x, y, 9, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x, y - 3, str(num))

    # The first four share one block. Draw them enlarged so the numbers can be read.
    inset = (48, 96, 196, 196)
    c.setFillColor(HexColor("#f3f6f1"))
    c.setStrokeColor(LINE)
    c.roundRect(inset[0], inset[1], inset[2] - inset[0], inset[3] - inset[1], 8, fill=1, stroke=1)
    c.setFillColor(STONE)
    c.setFont("Helvetica", 7)
    c.drawString(inset[0] + 8, inset[3] - 14, "Same block of De Portola")
    yy = inset[3] - 30
    for num, name, _addr, _lat, _lng in [s for s in STOPS if s[0] <= 4]:
        c.setFillColor(SAGE)
        c.circle(inset[0] + 16, yy + 2, 6, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(inset[0] + 16, yy, str(num))
        c.setFillColor(INK)
        c.setFont("Helvetica", 7)
        c.drawString(inset[0] + 28, yy - 1, name)
        yy -= 16

    c.setFillColor(STONE)
    c.setFont("Helvetica", 8)
    c.drawString(map_box[0] + 12, map_box[1] + 12, "Pins follow published card coordinates. Oak Mountain sits on Via Verde.")

    # Legend
    lx = 448
    c.setFillColor(INK)
    c.setFont("Times-Bold", 14)
    c.drawString(lx, height - 108, "The eleven stops")
    c.setFont("Helvetica", 8)
    c.setFillColor(STONE)
    c.drawString(lx, height - 122, "South to north, not alphabetical.")
    y = height - 146
    for num, name, addr, _lat, _lng in STOPS:
        c.setFillColor(SAGE)
        c.circle(lx + 8, y + 3, 7, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(lx + 8, y + 1, str(num))
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(lx + 22, y + 2, name)
        c.setFillColor(STONE)
        c.setFont("Helvetica", 8)
        c.drawString(lx + 22, y - 10, addr)
        y -= 28

    # Footer: logo + website
    c.setFillColor(SAGE)
    c.rect(0, 0, width, 62, fill=1, stroke=0)
    if LOGO.exists():
        c.drawImage(str(LOGO), 28, 10, width=118, height=48, mask="auto", preserveAspectRatio=True, anchor="c")
    c.setFillColor(white)
    c.setFont("Times-Bold", 12)
    c.drawString(168, 34, "bellieacreswine.com")
    c.setFont("Helvetica", 8)
    c.drawString(168, 18, "Independent Temecula wine guide  ·  /guides/de-portola-wine-trail/")
    c.drawRightString(width - 28, 26, "Confirm hours before you go.")

    c.showPage()
    c.save()
    print(OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
