from fastapi import APIRouter, HTTPException
from app.repositories import doors as doors_repo
from app.repositories import walls as repo
from app.schemas.estimate import DoorWidthsRequest

router = APIRouter()


@router.get("/walls")
def list_walls():
    return {"items": repo.list_walls()}


@router.get("/walls/{wall_id}")
def get_wall(wall_id: int):
    row = repo.get_wall(wall_id)
    if not row:
        raise HTTPException(404)
    return row


@router.get("/walls/{wall_id}/doors")
def list_wall_doors(wall_id: int):
    if not repo.get_wall(wall_id):
        raise HTTPException(404)
    return {"items": doors_repo.list_doors(wall_id)}


@router.put("/walls/{wall_id}/doors")
def replace_wall_doors(wall_id: int, body: DoorWidthsRequest):
    if not repo.get_wall(wall_id):
        raise HTTPException(404)
    return {"items": doors_repo.replace_doors(wall_id, body.widths)}
