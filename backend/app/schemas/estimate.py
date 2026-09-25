import math

from pydantic import BaseModel, field_validator


class EstimateRequest(BaseModel):
    wall_id: int
    roll_id: int
    save: bool = False
    note: str = ""
    # None: use the wall's persisted door widths; []: explicitly no doors
    door_widths: list[float] | None = None

    @field_validator("door_widths")
    @classmethod
    def _check_door_widths(cls, v):
        if v is None:
            return v
        for w in v:
            if not math.isfinite(w) or w < 0:
                raise ValueError("door widths must be finite and non-negative")
        return v


class DoorWidthsRequest(BaseModel):
    widths: list[float] = []

    @field_validator("widths")
    @classmethod
    def _check_widths(cls, v):
        for w in v:
            if not math.isfinite(w) or w < 0:
                raise ValueError("door widths must be finite and non-negative")
        return v
