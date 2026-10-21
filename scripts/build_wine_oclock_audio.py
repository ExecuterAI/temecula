#!/usr/bin/env python3
"""Rebuild Wine O'Clock narration from the JSON library.

Uses Andrew, the free neural voice, through edge-tts 7.3.1.
Run: uv run --with edge-tts==7.3.1 python scripts/build_wine_oclock_audio.py
No paid voice API. Edit the JSON, then run this again.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import edge_tts

ROOT = Path("/Users/executer/bellieacreswine")
DAYS = ROOT / "public/wine-oclock/content/days.json"
LESSONS = ROOT / "public/wine-oclock/content/lessons.json"
AUDIO = ROOT / "public/wine-oclock/audio"
VOICE = "en-US-AndrewMultilingualNeural"
RATE = "-8%"


def for_speech(text: str) -> str:
    """Andrew reads Bellie as bell-lie. The screen keeps Bellie. The voice says belly."""
    return text.replace("Bellie", "Belly").replace("bellie", "belly")


async def speak(text: str, dest: Path) -> None:
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(str(dest))
    print(dest.name, dest.stat().st_size)


async def main() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    for old in AUDIO.glob("*.m4a"):
        old.unlink()
    for day in json.loads(DAYS.read_text()):
        parts = [day["narration"]]
        if day.get("wineNote"):
            parts.append(day["wineNote"])
        await speak(for_speech(" ".join(parts)), AUDIO / f"{day['id']}.mp3")
    for lesson in json.loads(LESSONS.read_text()):
        await speak(for_speech(lesson["narration"]), AUDIO / f"lesson-{lesson['id']}.mp3")


if __name__ == "__main__":
    asyncio.run(main())
