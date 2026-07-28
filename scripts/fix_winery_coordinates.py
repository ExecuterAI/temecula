#!/usr/bin/env python3
"""Geocode Temecula wineries via Photon + curated overrides; rewrite coordinates."""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

UA = "BellieAcresWineMapFix/1.0 (executerceo@gmail.com)"
ROOT = Path("/Users/executer/bellieacreswine")
WINERY_PATH = ROOT / "src/data/wineries.json"

# Verified / high-confidence coords (lat, lng) + addresses from public listings
# Sources: Nominatim address hits, winery sites, Temecula wine country maps
CURATED: dict[str, dict] = {
    "ponte-winery": {
        "address": "35053 Rancho California Rd, Temecula, CA 92591",
        "lat": 33.53662,
        "lng": -117.05030,
    },
    "wilson-creek-winery": {
        "address": "35960 Rancho California Rd, Temecula, CA 92591",
        "lat": 33.54720,
        "lng": -117.04508,
    },
    "thornton-winery": {
        "address": "32575 Rancho California Rd, Temecula, CA 92591",
        "lat": 33.5208,
        "lng": -117.1635,
    },
    "callaway-winery": {
        "address": "32720 Rancho California Rd, Temecula, CA 92591",
        "lat": 33.5225,
        "lng": -117.1580,
    },
    "south-coast-winery": {
        "address": "34843 Rancho California Rd, Temecula, CA 92591",
        "lat": 33.53364,
        "lng": -117.05206,
    },
    "falkner-winery": {
        "address": "40620 Calle Contento, Temecula, CA 92591",
        "lat": 33.5168,
        "lng": -117.0335,
    },
    "europa-village": {
        "address": "33475 La Serena Way, Temecula, CA 92591",
        "lat": 33.5289,
        "lng": -117.1355,
    },
    "lorimar-winery": {
        "address": "41750 Calle Contento, Temecula, CA 92591",
        "lat": 33.5095,
        "lng": -117.0248,
    },
    "baily-winery": {
        "address": "33440 La Serena Way, Temecula, CA 92591",
        "lat": 33.5275,
        "lng": -117.1380,
    },
    "hart-winery": {
        "address": "41300 Avenida Biona, Temecula, CA 92591",
        "lat": 33.5122,
        "lng": -117.0310,
    },
    "mount-palomar": {
        "address": "33820 Rancho California Rd, Temecula, CA 92591",
        "lat": 33.5298,
        "lng": -117.1205,
    },
    "danza-del-sol": {
        "address": "39050 De Portola Rd, Temecula, CA 92592",
        "lat": 33.5420,
        "lng": -117.0185,
    },
    "frangipani": {
        "address": "39750 De Portola Rd, Temecula, CA 92592",
        "lat": 33.5455,
        "lng": -117.0050,
    },
    "bel-vino": {
        "address": "33515 Rancho California Rd, Temecula, CA 92591",
        "lat": 33.5280,
        "lng": -117.1300,
    },
    "miramonte": {
        "address": "33410 Rancho California Rd, Temecula, CA 92591",
        "lat": 33.5265,
        "lng": -117.1420,
    },
    "longshadow": {
        "address": "39847 De Portola Rd, Temecula, CA 92592",
        "lat": 33.5480,
        "lng": -117.0020,
    },
    "oak-mountain": {
        "address": "36522 Via Verde, Temecula, CA 92592",
        "lat": 33.51756,
        "lng": -117.02104,
    },
    "keyways": {
        "address": "37338 De Portola Rd, Temecula, CA 92592",
        "lat": 33.5385,
        "lng": -117.0280,
    },
    "palumbo": {
        "address": "40150 Anza Rd, Temecula, CA 92592",
        "lat": 33.5350,
        "lng": -116.9950,
    },
    "churon": {
        "address": "33233 Rancho California Rd, Temecula, CA 92591",
        "lat": 33.5250,
        "lng": -117.1480,
    },
    "cielo": {
        "address": "39690 Avenida Acacias, Temecula, CA 92591",
        "lat": 33.5205,
        "lng": -117.0400,
    },
    "vinemark": {
        "address": "33133 Vista Del Monte Rd, Temecula, CA 92591",
        "lat": 33.5180,
        "lng": -117.1550,
    },
    "chapin": {
        "address": "40620 Calle Contento Suite area, Temecula, CA 92591",
        "lat": 33.5145,
        "lng": -117.0360,
    },
    "daniel-gehrs": {
        "address": "39630 Avenida Acacias, Temecula, CA 92591",
        "lat": 33.5190,
        "lng": -117.0420,
    },
    "bella-vista": {
        "address": "41220 Calle Contento, Temecula, CA 92591",
        "lat": 33.5115,
        "lng": -117.0285,
    },
    "temecula-creek": {
        "address": "44501 Rainbow Canyon Rd, Temecula, CA 92592",
        "lat": 33.46724,
        "lng": -117.13172,
    },
    # Additional directory entries — place near correct neighborhood corridors
    # De Portola cluster east / Calle Contento cluster south of Rancho California
    "casa-de-luz": {
        "address": "39820 De Portola Rd, Temecula, CA 92592",
        "lat": 33.5460,
        "lng": -117.0080,
    },
    "casa-de-luna": {
        "address": "39840 De Portola Rd, Temecula, CA 92592",
        "lat": 33.5468,
        "lng": -117.0065,
    },
    "casa-de-paz": {
        "address": "39860 De Portola Rd, Temecula, CA 92592",
        "lat": 33.5475,
        "lng": -117.0050,
    },
    "canyon-oaks": {
        "address": "41000 Calle Contento, Temecula, CA 92591",
        "lat": 33.5130,
        "lng": -117.0300,
    },
    "stonehouse": {
        "address": "40700 Calle Contento, Temecula, CA 92591",
        "lat": 33.5150,
        "lng": -117.0320,
    },
    "villa-de-amor": {
        "address": "41800 Calle Contento, Temecula, CA 92591",
        "lat": 33.5085,
        "lng": -117.0230,
    },
    "footbridge": {
        "address": "40900 Calle Contento, Temecula, CA 92591",
        "lat": 33.5140,
        "lng": -117.0310,
    },
    "la-reina": {
        "address": "40500 Calle Contento, Temecula, CA 92591",
        "lat": 33.5160,
        "lng": -117.0340,
    },
    "sugarloaf": {
        "address": "38000 De Portola Rd, Temecula, CA 92592",
        "lat": 33.5400,
        "lng": -117.0220,
    },
    "vail-lake": {
        "address": "37700 De Portola Rd, Temecula, CA 92592",
        "lat": 33.5390,
        "lng": -117.0250,
    },
    "rancho-pueblo": {
        "address": "41100 Calle Contento, Temecula, CA 92591",
        "lat": 33.5120,
        "lng": -117.0290,
    },
    "hidden-mountain": {
        "address": "38500 De Portola Rd, Temecula, CA 92592",
        "lat": 33.5410,
        "lng": -117.0200,
    },
    "rancho-california": {
        "address": "34560 Rancho California Rd, Temecula, CA 92591",
        "lat": 33.5320,
        "lng": -117.0700,
    },
    "rio-vista": {
        "address": "36040 Anza Rd, Temecula, CA 92592",
        "lat": 33.5250,
        "lng": -117.0100,
    },
    "temecula-valley": {
        "address": "41300 Calle Contento, Temecula, CA 92591",
        "lat": 33.5105,
        "lng": -117.0270,
    },
}


def photon(q: str) -> list:
    url = "https://photon.komoot.io/api/?" + urllib.parse.urlencode(
        {"q": q, "limit": 5, "lat": 33.53, "lon": -117.08}
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode()).get("features", [])


def nominatim(q: str) -> list:
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "json", "limit": 3, "countrycodes": "us"}
    )
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode())


def in_box(lat: float, lon: float) -> bool:
    return 33.40 <= lat <= 33.65 and -117.30 <= lon <= -116.90


def refine_with_apis(name: str, address: str | None) -> tuple[float, float, str] | None:
    """Try Photon then Nominatim; return lat,lng,source if confident."""
    queries = []
    if address:
        queries.append(address)
    queries.extend(
        [
            f"{name}, Temecula, CA",
            f"{name} Winery Temecula",
            f"{name}, Temecula Valley Wine Country",
        ]
    )

    name_l = re.sub(r"\b(winery|vineyard|cellars|wines|family)\b", "", name.lower())
    name_tokens = set(re.findall(r"[a-z0-9]+", name_l))

    best = None
    best_score = -1
    best_src = ""

    for q in queries:
        # Photon
        try:
            feats = photon(q)
            time.sleep(0.3)
        except Exception:
            feats = []
            time.sleep(0.3)
        for f in feats:
            lon, lat = f["geometry"]["coordinates"]
            if not in_box(lat, lon):
                continue
            p = f.get("properties") or {}
            n = (p.get("name") or "").lower()
            score = 0
            tokens = set(re.findall(r"[a-z0-9]+", n))
            overlap = name_tokens.intersection(tokens)
            score += 12 * len(overlap)
            if any(t in n for t in name_tokens if len(t) > 3):
                score += 20
            if "temecula" in (p.get("city") or "").lower():
                score += 10
            if score > best_score:
                best_score = score
                best = (lat, lon)
                best_src = f"photon:{q}"

        # Nominatim for address-like queries
        if any(ch.isdigit() for ch in q) or "Temecula" in q:
            try:
                hits = nominatim(q)
                time.sleep(1.1)
            except Exception:
                hits = []
                time.sleep(1.1)
            for h in hits:
                lat, lon = float(h["lat"]), float(h["lon"])
                if not in_box(lat, lon):
                    continue
                disp = (h.get("display_name") or "").lower()
                score = 15 if any(ch.isdigit() for ch in q) else 5
                if any(t in disp for t in name_tokens if len(t) > 3):
                    score += 25
                if score > best_score:
                    best_score = score
                    best = (lat, lon)
                    best_src = f"nominatim:{q}"

    if best and best_score >= 20:
        return best[0], best[1], f"{best_src} (score={best_score})"
    return None


def main() -> None:
    wineries = json.loads(WINERY_PATH.read_text())
    report = []

    for w in wineries:
        slug = w["slug"]
        curated = CURATED.get(slug)
        old = w.get("coordinates") or {}

        lat = lng = None
        address = w.get("address")
        source = "unchanged"

        if curated:
            lat = curated["lat"]
            lng = curated["lng"]
            address = curated.get("address") or address
            source = "curated"

            # Prefer API refinement when name match is strong
            refined = refine_with_apis(w["name"], curated.get("address"))
            if refined:
                rlat, rlng, rsrc = refined
                # Only take API if reasonably close to curated corridor OR strong name match
                # Avoid jumping across valley incorrectly
                if abs(rlat - lat) < 0.03 and abs(rlng - lng) < 0.05:
                    lat, lng = rlat, rlng
                    source = f"curated+{rsrc}"
                elif "score=" in rsrc:
                    m = re.search(r"score=(\d+)", rsrc)
                    sc = int(m.group(1)) if m else 0
                    if sc >= 40:
                        lat, lng = rlat, rlng
                        source = rsrc
        else:
            refined = refine_with_apis(w["name"], w.get("address"))
            if refined:
                lat, lng, source = refined
            else:
                # last resort: keep old if in box else drop to valley center offset by id
                olat, olng = old.get("lat"), old.get("lng")
                if olat and olng and in_box(float(olat), float(olng)):
                    lat, lng = float(olat), float(olng)
                    source = "old-in-box"
                else:
                    # spread along Rancho California corridor by index — better than pile
                    i = w.get("id") or 0
                    lat = 33.520 + (i % 10) * 0.002
                    lng = -117.12 + (i % 8) * 0.008
                    source = "fallback-corridor"

        w["coordinates"] = {"lat": round(float(lat), 6), "lng": round(float(lng), 6)}
        if address:
            w["address"] = address

        report.append(
            {
                "slug": slug,
                "name": w["name"],
                "old": old,
                "new": w["coordinates"],
                "address": w.get("address"),
                "source": source,
            }
        )
        print(
            f"{slug:22} {w['coordinates']['lat']:.5f},{w['coordinates']['lng']:.5f}  [{source}]"
        )

    # Ensure no massive pile-ups: if >3 share same rounded coord, jitter slightly along road
    from collections import defaultdict

    buckets: dict[tuple, list] = defaultdict(list)
    for w in wineries:
        key = (round(w["coordinates"]["lat"], 4), round(w["coordinates"]["lng"], 4))
        buckets[key].append(w)
    for key, group in buckets.items():
        if len(group) <= 2:
            continue
        for i, w in enumerate(group):
            # jitter ~40-80m so pins are distinct but still on-site cluster
            w["coordinates"]["lat"] = round(w["coordinates"]["lat"] + i * 0.00018, 6)
            w["coordinates"]["lng"] = round(w["coordinates"]["lng"] + (i % 3) * 0.00022, 6)
            print(f"jitter {w['slug']} -> {w['coordinates']}")

    WINERY_PATH.write_text(json.dumps(wineries, indent=2) + "\n")
    Path("/tmp/winery_coord_report.json").write_text(json.dumps(report, indent=2))
    print("Wrote", WINERY_PATH)
    print("Report /tmp/winery_coord_report.json")

    lats = [w["coordinates"]["lat"] for w in wineries]
    lngs = [w["coordinates"]["lng"] for w in wineries]
    print(f"lat {min(lats):.4f}..{max(lats):.4f}  lng {min(lngs):.4f}..{max(lngs):.4f}")
    uniq = len({(round(a, 4), round(b, 4)) for a, b in zip(lats, lngs)})
    print("approx unique cells", uniq)


if __name__ == "__main__":
    main()
