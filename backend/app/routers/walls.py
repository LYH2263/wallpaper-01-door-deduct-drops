from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.engines.wallpaper_math import effective_perimeter
from app.repositories import walls as repo

router = APIRouter()


class DoorsUpdate(BaseModel):
    doors: list[float]


@router.get("/walls")
def list_walls():
    return {"items": repo.list_walls()}


@router.get("/walls/{wall_id}")
def get_wall(wall_id: int):
    row = repo.get_wall(wall_id)
    if not row:
        raise HTTPException(404)
    return row


@router.put("/walls/{wall_id}/doors")
def put_doors(wall_id: int, body: DoorsUpdate):
    wall = repo.get_wall(wall_id)
    if not wall:
        raise HTTPException(404)
    try:
        effective_perimeter(wall["perimeter"], body.doors)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    repo.update_doors(wall_id, body.doors)
    return repo.get_wall(wall_id)
