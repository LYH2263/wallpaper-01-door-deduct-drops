from pydantic import BaseModel


class EstimateRequest(BaseModel):
    wall_id: int
    roll_id: int
    save: bool = False
    note: str = ""
    door_widths: list[float] | None = None
