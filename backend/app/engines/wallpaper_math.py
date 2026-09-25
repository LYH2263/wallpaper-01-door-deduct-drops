"""Wallpaper rolls: perimeter strips, pattern repeat on drop length, strips per roll."""

from app.engines.helpers import ceil_units, floor_units


def effective_perimeter_m(perimeter: float, door_widths=None) -> float:
    """Perimeter left after subtracting door openings; identical to perimeter when no doors."""
    doors_total = sum(float(w) for w in door_widths) if door_widths else 0.0
    return float(perimeter) - doors_total


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
    doors = [float(w) for w in door_widths] if door_widths else []
    doors_total = sum(doors)
    effective_perimeter = float(perimeter) - doors_total
    if effective_perimeter <= 0:
        raise ValueError("effective perimeter must be positive")
    drops = ceil_units(effective_perimeter / float(roll_width))
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
        "doors_total_m": round(doors_total, 3),
        "effective_perimeter_m": round(effective_perimeter, 3),
    }
