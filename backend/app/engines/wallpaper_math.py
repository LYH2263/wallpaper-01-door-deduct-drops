"""Wallpaper rolls: perimeter strips, pattern repeat on drop length, strips per roll."""

import math

from app.engines.helpers import ceil_units, floor_units


def clean_door_widths(door_widths) -> list:
    """Normalize registered door widths; negative or non-finite widths are invalid."""
    doors = []
    for w in door_widths or []:
        w = float(w)
        if not math.isfinite(w) or w < 0:
            raise ValueError("invalid door width")
        doors.append(w)
    return doors


def effective_perimeter(perimeter: float, door_widths=None) -> float:
    """Wall perimeter minus the registered door widths; must stay positive."""
    effective = float(perimeter) - sum(clean_door_widths(door_widths))
    if effective <= 0:
        raise ValueError("effective perimeter must be positive")
    return effective


def roll_count(
    perimeter: float,
    height: float,
    roll_width: float,
    roll_length: float,
    pattern_cm: float,
    door_widths=None,
) -> dict:
    if roll_width <= 0 or roll_length <= 0:
        raise ValueError("invalid roll size")
    doors = clean_door_widths(door_widths)
    effective = effective_perimeter(perimeter, doors)
    drops = ceil_units(effective / float(roll_width))
    pattern_m = max(0.0, float(pattern_cm) / 100.0)
    drop_len = float(height) + pattern_m
    if drop_len <= 0:
        raise ValueError("invalid drop length")
    strips_per_roll = max(1, floor_units(float(roll_length) / drop_len))
    rolls = ceil_units(drops / strips_per_roll)
    return {
        "drops": drops,
        "drop_len_m": round(drop_len, 3),
        "pattern_m": round(pattern_m, 3),
        "strips_per_roll": strips_per_roll,
        "rolls": rolls,
        "door_widths": doors,
        "door_total_m": round(sum(doors), 3),
        "effective_perimeter_m": round(effective, 3),
    }
