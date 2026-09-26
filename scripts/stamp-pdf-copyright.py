"""Stamp Bellie Acres Wine seal + copyright on planner PDFs."""
from pathlib import Path
import shutil
from datetime import datetime

import pymupdf

SEAL = Path("/Users/executer/bellieacreswine/public/images/bellie-acres-seal.jpg")
YEAR = datetime.now().year
NOTICE = f"© {YEAR} Bellie Acres Wine. All rights reserved."
SAGE = (74 / 255, 94 / 255, 78 / 255)

FILES = [
    Path("/Users/executer/bellieacreswine/public/downloads/temecula-wine-day-planner.pdf"),
    Path("/Users/executer/bellieacreswine/public/downloads/temecula-weekend-planner.pdf"),
]


def stamp(path: Path) -> None:
    bak = path.with_suffix(".pdf.bak")
    if not bak.exists():
        shutil.copy2(path, bak)

    doc = pymupdf.open(path)
    for i, page in enumerate(doc):
        w, h = page.rect.width, page.rect.height
        if i == 0:
            size = 68
            x0 = (w - size) / 2
            y0 = h - 118
            page.insert_image(pymupdf.Rect(x0, y0, x0 + size, y0 + size), filename=str(SEAL))
            tw = pymupdf.get_text_length(NOTICE, fontname="helv", fontsize=8)
            page.insert_text(
                pymupdf.Point((w - tw) / 2, y0 + size + 14),
                NOTICE,
                fontname="helv",
                fontsize=8,
                color=SAGE,
            )
        else:
            size = 16
            x0 = 48
            y0 = h - 28
            page.insert_image(pymupdf.Rect(x0, y0, x0 + size, y0 + size), filename=str(SEAL))
            page.insert_text(
                pymupdf.Point(x0 + size + 6, y0 + 12),
                NOTICE,
                fontname="helv",
                fontsize=7,
                color=SAGE,
            )

    doc.set_metadata(
        {
            **doc.metadata,
            "author": "Bellie Acres Wine",
            "title": "Temecula Wine Day Planner",
            "subject": f"© {YEAR} Bellie Acres Wine. All rights reserved.",
            "modDate": pymupdf.get_pdf_now(),
        }
    )
    tmp = path.with_suffix(".stamped.pdf")
    doc.save(tmp, incremental=False, deflate=True)
    doc.close()
    tmp.replace(path)
    print("stamped", path, "bytes", path.stat().st_size)


def main() -> None:
    for p in FILES:
        stamp(p)


if __name__ == "__main__":
    main()
