from fastapi import HTTPException

from app.engines.wallpaper_math import roll_count
from app.repositories import history, rolls, walls


def run_estimate(wall_id: int, roll_id: int, save: bool, note: str, door_widths=None):
    wall = walls.get_wall(wall_id)
    if not wall:
        raise HTTPException(404, "wall not found")
    roll = rolls.get_roll(roll_id)
    if not roll:
        raise HTTPException(404, "roll not found")
    if wall.get("data_quality") == "dirty" or roll.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty seed entity")

    # No explicit door widths in the request -> use the doors registered on the wall.
    doors = wall.get("doors") if door_widths is None else door_widths
    try:
        calc = roll_count(
            wall["perimeter"], wall["height"], roll["width"], roll["length"], roll["pattern_cm"], doors
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    run_id = None
    if save:
        run_id = history.insert_run(wall_id, roll_id, {**calc, "wall_id": wall_id, "roll_id": roll_id}, note)
    return {"wall": wall, "roll": roll, "run_id": run_id, **calc}
