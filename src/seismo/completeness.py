"""Magnitude-of-completeness utilities.

The MAXC implementation here is intentionally small and dependency-free so the
teaching project can run in GitHub Actions. It is suitable for demonstrations
and exploratory quality control, not as the sole completeness method in a
scientific publication.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from math import floor
from typing import Iterable, Mapping, Sequence


def _month_start(value: datetime) -> datetime:
    return datetime(value.year, value.month, 1)


def _add_months(value: datetime, months: int) -> datetime:
    index = value.year * 12 + value.month - 1 + months
    return datetime(index // 12, index % 12 + 1, 1)


def estimate_mc_maxc(magnitudes: Iterable[float], bin_width: float = 0.1) -> dict:
    """Estimate Mc using the maximum-curvature histogram bin.

    Magnitudes are rounded to the nearest configured bin. If multiple bins have
    the same maximum frequency, the lower magnitude is selected.
    """
    values = [float(value) for value in magnitudes]
    if not values:
        raise ValueError("At least one magnitude is required")
    if bin_width <= 0:
        raise ValueError("bin_width must be positive")

    decimals = max(0, len(f"{bin_width:.10f}".rstrip("0").split(".")[-1]))
    bins = [round(round(value / bin_width) * bin_width, decimals) for value in values]
    counts = Counter(bins)
    max_count = max(counts.values())
    mc = min(magnitude for magnitude, count in counts.items() if count == max_count)

    histogram = [
        {"magnitude": magnitude, "count": counts[magnitude]}
        for magnitude in sorted(counts)
    ]
    return {
        "method": "MAXC",
        "mc": mc,
        "bin_width": bin_width,
        "sample_count": len(values),
        "peak_count": max_count,
        "histogram": histogram,
    }


def monthly_moving_mc(
    events: Sequence[Mapping[str, object]],
    window_months: int = 3,
    bin_width: float = 0.1,
    minimum_samples: int = 50,
) -> list[dict]:
    """Calculate Mc once per month using a moving calendar-month window.

    Each event requires ``time`` (ISO string or datetime) and ``magnitude``.
    The returned date is the final month included in each window.
    """
    if window_months < 1:
        raise ValueError("window_months must be at least 1")

    normalized: list[tuple[datetime, float]] = []
    for event in events:
        raw_time = event["time"]
        when = raw_time if isinstance(raw_time, datetime) else datetime.fromisoformat(str(raw_time).replace("Z", "+00:00"))
        if when.tzinfo is not None:
            when = when.replace(tzinfo=None)
        normalized.append((when, float(event["magnitude"])))

    if not normalized:
        return []

    first_month = _month_start(min(time for time, _ in normalized))
    last_month = _month_start(max(time for time, _ in normalized))
    current_end = _add_months(first_month, window_months - 1)
    results: list[dict] = []

    while current_end <= last_month:
        window_start = _add_months(current_end, -(window_months - 1))
        next_month = _add_months(current_end, 1)
        magnitudes = [
            magnitude
            for time, magnitude in normalized
            if window_start <= time < next_month
        ]

        if magnitudes:
            estimate = estimate_mc_maxc(magnitudes, bin_width=bin_width)
            sample_count = estimate["sample_count"]
            quality = "ok" if sample_count >= minimum_samples else "low-sample"
            results.append(
                {
                    "window_start": window_start.date().isoformat(),
                    "window_end": current_end.date().isoformat(),
                    "mc": estimate["mc"],
                    "sample_count": sample_count,
                    "quality": quality,
                }
            )
        current_end = _add_months(current_end, 1)

    return results


def magnitude_frequency(magnitudes: Iterable[float], bin_width: float = 0.1) -> list[dict]:
    """Return non-cumulative and cumulative frequency by magnitude bin."""
    estimate = estimate_mc_maxc(magnitudes, bin_width=bin_width)
    histogram = estimate["histogram"]
    cumulative = 0
    output: list[dict] = []
    for item in reversed(histogram):
        cumulative += int(item["count"])
        output.append(
            {
                "magnitude": item["magnitude"],
                "count": item["count"],
                "cumulative": cumulative,
            }
        )
    return list(reversed(output))
