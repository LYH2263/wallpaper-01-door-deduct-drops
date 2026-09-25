import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app import seed
from app.db import connect
from app.repositories import doors, history
from app.schemas.estimate import EstimateRequest
from app.services import estimate_service


@pytest.fixture
def db(monkeypatch, tmp_path):
    import app.db as db_module

    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test.db")
    seed.init_db()


def count_runs() -> int:
    conn = connect()
    try:
        return conn.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]
    finally:
        conn.close()


def test_negative_door_width_rejected_by_schema(db):
    with pytest.raises(ValidationError):
        EstimateRequest(wall_id=1, roll_id=1, door_widths=[-0.1])
    with pytest.raises(ValidationError):
        EstimateRequest(wall_id=1, roll_id=1, door_widths=[float("nan")])


def test_no_doors_matches_pre_change_result(db):
    out = estimate_service.run_estimate(1, 1, False, "")
    assert out["drops"] == 31
    assert out["rolls"] == 11
    assert out["door_widths"] == []
    assert out["effective_perimeter_m"] == 16.0


def test_effective_perimeter_non_positive_fails_without_run(db):
    before = count_runs()
    with pytest.raises(HTTPException) as exc:
        estimate_service.run_estimate(1, 1, True, "", [16.0])
    assert exc.value.status_code == 422
    assert count_runs() == before

    with pytest.raises(HTTPException) as exc:
        estimate_service.run_estimate(1, 1, True, "", [20.0])
    assert exc.value.status_code == 422
    assert count_runs() == before


def test_persisted_run_snapshots_doors(db):
    out = estimate_service.run_estimate(1, 1, True, "有门", [0.9, 0.8])
    # 16.0 - 1.7 = 14.3; /0.53 = 26.98 -> 27 drops; ceil(27/3) = 9 rolls
    assert out["effective_perimeter_m"] == 14.3
    assert out["drops"] == 27
    assert out["rolls"] == 9

    run = history.get_run(out["run_id"])
    result = run["result"]
    assert result["door_widths"] == [0.9, 0.8]
    assert result["doors_total_m"] == 1.7
    assert result["effective_perimeter_m"] == 14.3
    assert result["drops"] == 27
    assert result["rolls"] == 9


def test_later_door_edits_do_not_rewrite_old_run(db):
    run_id = estimate_service.run_estimate(1, 1, True, "", [0.9, 0.8])["run_id"]

    doors.replace_doors(1, [2.0])
    run = history.get_run(run_id)
    assert run["result"]["door_widths"] == [0.9, 0.8]
    assert run["result"]["effective_perimeter_m"] == 14.3
    assert run["result"]["drops"] == 27
    assert run["result"]["rolls"] == 9


def test_none_uses_persisted_doors_explicit_empty_overrides(db):
    doors.replace_doors(1, [0.53])
    pulled = estimate_service.run_estimate(1, 1, False, "", None)
    # 16.0 - 0.53 = 15.47; /0.53 = 29.19 -> 30 drops
    assert pulled["door_widths"] == [0.53]
    assert pulled["drops"] == 30

    explicit_empty = estimate_service.run_estimate(1, 1, False, "", [])
    assert explicit_empty["door_widths"] == []
    assert explicit_empty["drops"] == 31

    doors.replace_doors(1, [])
    cleared = estimate_service.run_estimate(1, 1, False, "", None)
    assert cleared["drops"] == 31
    assert cleared["rolls"] == 11


def test_get_run_missing_returns_none(db):
    assert history.get_run(9999) is None
