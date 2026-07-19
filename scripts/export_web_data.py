"""Convert the sample catalog into a compact JSON payload for the website."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from seismo.completeness import estimate_mc_maxc, magnitude_frequency, monthly_moving_mc

INPUT = ROOT / "data" / "sample" / "catalog.csv"
OUTPUT = ROOT / "site" / "data" / "summary.json"


def read_catalog() -> list[dict[str, object]]:
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing {INPUT}. Run scripts/generate_sample_catalog.py first."
        )
    events: list[dict[str, object]] = []
    with INPUT.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            events.append(
                {
                    "event_id": row["event_id"],
                    "time": row["time"],
                    "latitude": float(row["latitude"]),
                    "longitude": float(row["longitude"]),
                    "depth_km": float(row["depth_km"]),
                    "magnitude": float(row["magnitude"]),
                    "data_type": row["data_type"],
                }
            )
    return events


def main() -> None:
    events = read_catalog()
    magnitudes = [float(event["magnitude"]) for event in events]
    overall = estimate_mc_maxc(magnitudes, bin_width=0.1)
    moving = monthly_moving_mc(
        events,
        window_months=3,
        bin_width=0.1,
        minimum_samples=50,
    )
    payload = {
        "metadata": {
            "title": "OpenCode 地震目錄與 Mc 互動實驗室",
            "data_notice": "本頁資料由固定亂數種子產生，僅供教學展示，不代表正式地震觀測。",
            "analysis_version": "1.0.0",
            "mc_method": "MAXC",
            "bin_width": 0.1,
            "window_months": 3,
            "calculation_interval": "monthly",
        },
        "summary": {
            "event_count": len(events),
            "date_start": min(str(event["time"]) for event in events)[:10],
            "date_end": max(str(event["time"]) for event in events)[:10],
            "magnitude_min": min(magnitudes),
            "magnitude_max": max(magnitudes),
            "overall_mc": overall["mc"],
            "latest_mc": moving[-1]["mc"] if moving else None,
            "latest_mc_samples": moving[-1]["sample_count"] if moving else 0,
        },
        "moving_mc": moving,
        "magnitude_frequency": magnitude_frequency(magnitudes, bin_width=0.1),
        "events": events,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote web data to {OUTPUT}")


if __name__ == "__main__":
    main()
