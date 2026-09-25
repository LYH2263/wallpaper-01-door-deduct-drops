from datetime import datetime, timezone

from app.db import get_conn


def list_doors(wall_id: int):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, wall_id, width FROM wall_doors WHERE wall_id=? ORDER BY id",
            (wall_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def replace_doors(wall_id: int, widths: list[float]):
    """Replace the whole door list of a wall in one transaction."""
    now = datetime.now(timezone.utc).isoformat()
    with get_conn() as conn:
        conn.execute("DELETE FROM wall_doors WHERE wall_id=?", (wall_id,))
        conn.executemany(
            "INSERT INTO wall_doors(wall_id,width,created_at) VALUES (?,?,?)",
            [(wall_id, float(w), now) for w in widths],
        )
        rows = conn.execute(
            "SELECT id, wall_id, width FROM wall_doors WHERE wall_id=? ORDER BY id",
            (wall_id,),
        ).fetchall()
        return [dict(r) for r in rows]
