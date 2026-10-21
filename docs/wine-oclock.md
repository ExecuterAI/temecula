# Wine O’Clock by Bellie Acres Wine

A separate installable page at `/wine-oclock/`. It does not replace the Bellie Acres Wine homepage.

## Update the words

Edit the JSON files in `public/wine-oclock/content/`.

- `days.json` — the 30 daily moments
- `varietals.json` — The Wine Guide
- `lessons.json` — Wine in 60 Seconds
- `pairings.json` — Pairings for the Occasion
- `quotes.json` — lines for The Wine Philosopher

Then rebuild the spoken files, if you want the voice to match the new words:

```bash
uv run --with edge-tts==7.3.1 python scripts/build_wine_oclock_audio.py
```

That uses Andrew, a free neural voice (`en-US-AndrewMultilingualNeural`). It does not call a paid service. Reed, the first Mac voice, sounded mechanical and has been replaced.

## Deploy

The site builds with `npm run build` and publishes from `main` on Netlify. The homepage is not part of this app. The only site link is in the footer: “Explore Wine O’Clock by Bellie Acres Wine.”

## What stays on the phone

Preferences, favorites, and “skip today” are stored in the browser under `bellie-wine-oclock`. There is no account. Reset is in Preferences.

## Known limits

- A reminder invites the listener to open the app. It does not start the audio.
- This is not an App Store app. An iPhone will not reliably play a custom sound at an exact time while the page is closed.
- Add to Home Screen works from Safari: Share, then Add to Home Screen. The page only says it is installed when it was actually opened from that icon.
- The musical signatures are original tones, not licensed band recordings. Nothing plays until Play is pressed.
- Offline works for pages and sounds this phone has already loaded. A voice file that was never opened needs a connection the first time.
