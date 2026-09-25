import json

from app.db import connect


def _with_doors(row) -> dict:
    d = dict(row)
    try:
        d["doors"] = [float(w) for w in json.loads(d.pop("doors_json") or "[]")]
    except (TypeError, ValueError):
        d["doors"] = []
    return d


def list_walls():
    conn = connect()
    try:
        return [_with_doors(r) for r in conn.execute("SELECT * FROM walls ORDER BY id").fetchall()]
    finally:
        conn.close()


def get_wall(wid: int):
    conn = connect()
    try:
        row = conn.execute("SELECT * FROM walls WHERE id=?", (wid,)).fetchone()
        return _with_doors(row) if row else None
    finally:
        conn.close()


def update_doors(wid: int, doors) -> None:
    conn = connect()
    try:
        conn.execute(
            "UPDATE walls SET doors_json=? WHERE id=?",
            (json.dumps([float(w) for w in doors], ensure_ascii=False), wid),
        )
        conn.commit()
    finally:
        conn.close()
