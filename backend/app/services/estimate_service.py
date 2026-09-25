from fastapi import HTTPException

from app.engines.wallpaper_math import effective_perimeter_m, roll_count
from app.repositories import doors, history, rolls, walls


def run_estimate(wall_id: int, roll_id: int, save: bool, note: str, door_widths=None):
    wall = walls.get_wall(wall_id)
    if not wall:
        raise HTTPException(404, "wall not found")
    roll = rolls.get_roll(roll_id)
    if not roll:
        raise HTTPException(404, "roll not found")
    if wall.get("data_quality") == "dirty" or roll.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty seed entity")

    # None means "use the wall's persisted door openings"; an explicit list (even empty) wins.
    if door_widths is None:
        door_widths = [d["width"] for d in doors.list_doors(wall_id)]

    if effective_perimeter_m(wall["perimeter"], door_widths) <= 0:
        raise HTTPException(422, "effective perimeter must be positive")

    calc = roll_count(
        wall["perimeter"],
        wall["height"],
        roll["width"],
        roll["length"],
        roll["pattern_cm"],
        door_widths,
    )
    run_id = None
    if save:
        run_id = history.insert_run(
            wall_id, roll_id, {**calc, "wall_id": wall_id, "roll_id": roll_id}, note
        )
    return {"wall": wall, "roll": roll, "run_id": run_id, **calc}
