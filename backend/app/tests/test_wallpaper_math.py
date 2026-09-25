import pytest

from app.engines.wallpaper_math import roll_count


def test_plain_master_bed():
    r = roll_count(16.0, 2.7, 0.53, 10.0, 0)
    assert r["drops"] == 31
    assert r["drop_len_m"] == 2.7
    assert r["strips_per_roll"] == 3
    assert r["rolls"] == 11


def test_pattern_wall():
    r = roll_count(20.0, 2.8, 0.53, 10.0, 64)
    assert r["drops"] == 38
    assert r["drop_len_m"] == 3.44
    assert r["strips_per_roll"] == 2
    assert r["rolls"] == 19


def test_door_deducts_drops():
    r = roll_count(16.0, 2.7, 0.53, 10.0, 0, [0.9])
    assert r["door_widths"] == [0.9]
    assert r["door_total_m"] == 0.9
    assert r["effective_perimeter_m"] == 15.1
    assert r["drops"] == 29
    assert r["drop_len_m"] == 2.7
    assert r["strips_per_roll"] == 3
    assert r["rolls"] == 10


def test_multiple_doors_deduct():
    r = roll_count(20.0, 2.8, 0.53, 10.0, 64, [0.9, 0.8])
    assert r["door_total_m"] == 1.7
    assert r["effective_perimeter_m"] == 18.3
    assert r["drops"] == 35
    assert r["strips_per_roll"] == 2
    assert r["rolls"] == 18


def test_no_doors_matches_base():
    base = roll_count(16.0, 2.7, 0.53, 10.0, 0)
    for doors in (None, [], [0.0], [0.0, 0.0]):
        r = roll_count(16.0, 2.7, 0.53, 10.0, 0, doors)
        assert r["drops"] == base["drops"]
        assert r["drop_len_m"] == base["drop_len_m"]
        assert r["strips_per_roll"] == base["strips_per_roll"]
        assert r["rolls"] == base["rolls"]


def test_negative_door_rejected():
    with pytest.raises(ValueError):
        roll_count(16.0, 2.7, 0.53, 10.0, 0, [-0.5])


def test_non_finite_door_rejected():
    with pytest.raises(ValueError):
        roll_count(16.0, 2.7, 0.53, 10.0, 0, [float("nan")])
    with pytest.raises(ValueError):
        roll_count(16.0, 2.7, 0.53, 10.0, 0, [float("inf")])


def test_effective_perimeter_nonpositive_rejected():
    with pytest.raises(ValueError):
        roll_count(16.0, 2.7, 0.53, 10.0, 0, [16.0])
    with pytest.raises(ValueError):
        roll_count(16.0, 2.7, 0.53, 10.0, 0, [10.0, 6.5])
