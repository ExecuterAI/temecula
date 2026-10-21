#!/usr/bin/env python3
"""Build Wine O'Clock narration from public/wine-oclock/content/days.json.

Voice is local and replaceable. Edit the JSON, then run this script.
No paid voice API.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path("/Users/executer/bellieacreswine")
DAYS = ROOT / "public/wine-oclock/content/days.json"
LESSONS = ROOT / "public/wine-oclock/content/lessons.json"
AUDIO = ROOT / "public/wine-oclock/audio"
VOICE = "Reed (English (US))"
RATE = "148"


def speak(text: str, dest: Path) -> None:
    aiff = dest.with_suffix(".aiff")
    subprocess.run(["say", "-v", VOICE, "-r", RATE, "-o", str(aiff), text], check=True)
    subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", str(aiff), str(dest)], check=True)
    aiff.unlink()
    print(dest.name, dest.stat().st_size)


def main() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    for day in json.loads(DAYS.read_text()):
        parts = [day["narration"]]
        if day.get("wineNote"):
            parts.append(day["wineNote"])
        speak(" ".join(parts), AUDIO / f"{day['id']}.m4a")
    for lesson in json.loads(LESSONS.read_text()):
        speak(lesson["narration"], AUDIO / f"lesson-{lesson['id']}.m4a")


if __name__ == "__main__":
    main()
