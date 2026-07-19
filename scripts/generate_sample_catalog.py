"""Generate a deterministic synthetic earthquake catalog for the demo site."""

from __future__ import annotations

import csv
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "sample" / "catalog.csv"
SEED = 20260719


def add_months(value: datetime, months: int) -> datetime:
    index = value.year * 12 + value.month - 1 + months
    return datetime(index // 12, index % 12 + 1, 1)


def generate_catalog() -> list[dict[str, object]]:
    rng = random.Random(SEED)
    start = datetime(2025, 1, 1)
    rows: list[dict[str, object]] = []
    event_number = 1

    for month_index in range(18):
        month_start = add_months(start, month_index)
        next_month = add_months(month_start, 1)
        month_seconds = int((next_month - month_start).total_seconds())
        expected_mc = 1.55 + 0.18 * math.sin(month_index / 2.4)

        for _ in range(24):
            when = month_start + timedelta(seconds=rng.randrange(month_seconds))
            if rng.random() < 0.16:
                magnitude = max(0.5, expected_mc - rng.uniform(0.1, 0.8))
            else:
                magnitude = min(6.4, expected_mc + rng.expovariate(1.35))

            rows.append(
                {
                    "event_id": f"SYN{event_number:05d}",
                    "time": when.isoformat(timespec="seconds") + "Z",
                    "latitude": round(rng.uniform(21.65, 25.35), 4),
                    "longitude": round(rng.uniform(119.75, 122.35), 4),
                    "depth_km": round(rng.uniform(4.0, 38.0), 1),
                    "magnitude": round(magnitude, 1),
                    "data_type": "synthetic-demo",
                }
            )
            event_number += 1

    rows.sort(key=lambda row: str(row["time"]))
    return rows


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rows = generate_catalog()
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} synthetic events to {OUTPUT}")


if __name__ == "__main__":
    main()
