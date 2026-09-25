import os
import tempfile

os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="wallpaper-test-"))

import pytest
from fastapi import HTTPException

from app import seed
from app.repositories import history
from app.repositories import walls as walls_repo
from app.services import estimate_service


def setup_module():
    seed.init_db()


def _run_count():
    return len(history.list_runs(10000))


def test_estimate_without_doors_matches_base():
    walls_repo.update_doors(1, [])
    out = estimate_service.run_estimate(1, 1, False, "")
    assert out["drops"] == 31
    assert out["rolls"] == 11
    assert out["door_widths"] == []
    assert out["effective_perimeter_m"] == 16.0


def test_saved_run_stores_doors_effective_perimeter_drops_rolls():
    walls_repo.update_doors(1, [])
    out = estimate_service.run_estimate(1, 1, True, "带门", [0.9, 0.8])
    assert out["run_id"]
    assert out["drops"] == 27
    assert out["rolls"] == 9
    run = history.get_run(out["run_id"])
    assert run["result"]["door_widths"] == [0.9, 0.8]
    assert run["result"]["door_total_m"] == 1.7
    assert run["result"]["effective_perimeter_m"] == 14.3
    assert run["result"]["drops"] == 27
    assert run["result"]["rolls"] == 9


def test_estimate_uses_wall_doors_by_default():
    walls_repo.update_doors(1, [0.9])
    try:
        out = estimate_service.run_estimate(1, 1, False, "")
        assert out["door_widths"] == [0.9]
        assert out["effective_perimeter_m"] == 15.1
        assert out["drops"] == 29
        assert out["rolls"] == 10
    finally:
        walls_repo.update_doors(1, [])


def test_negative_door_fails_without_history_row():
    before = _run_count()
    with pytest.raises(HTTPException):
        estimate_service.run_estimate(1, 1, True, "", [-0.5])
    assert _run_count() == before


def test_effective_perimeter_nonpositive_fails_without_history_row():
    before = _run_count()
    with pytest.raises(HTTPException):
        estimate_service.run_estimate(1, 1, True, "", [16.0])
    with pytest.raises(HTTPException):
        estimate_service.run_estimate(1, 1, True, "", [20.0])
    assert _run_count() == before


def test_editing_wall_doors_does_not_rewrite_old_run():
    walls_repo.update_doors(1, [])
    out = estimate_service.run_estimate(1, 1, True, "", [0.9])
    walls_repo.update_doors(1, [0.8, 0.7])
    try:
        run = history.get_run(out["run_id"])
        assert run["result"]["door_widths"] == [0.9]
        assert run["result"]["drops"] == 29
        assert run["result"]["rolls"] == 10
    finally:
        walls_repo.update_doors(1, [])
