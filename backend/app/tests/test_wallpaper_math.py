import pytest

from app.engines.wallpaper_math import effective_perimeter_m, roll_count


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


def test_no_doors_matches_baseline():
    base = roll_count(16.0, 2.7, 0.53, 10.0, 0)
    assert roll_count(16.0, 2.7, 0.53, 10.0, 0, None)["drops"] == base["drops"]
    assert roll_count(16.0, 2.7, 0.53, 10.0, 0, [])["rolls"] == base["rolls"]
    zero_doors = roll_count(16.0, 2.7, 0.53, 10.0, 0, [0.0, 0.0])
    assert zero_doors["drops"] == base["drops"]
    assert zero_doors["rolls"] == base["rolls"]
    assert effective_perimeter_m(16.0, [0.0]) == 16.0


def test_doors_reduce_drops():
    # 16.0 - 1.06 = 14.94; /0.53 = 28.19 -> 29 drops; ceil(29/3) = 10 rolls
    r = roll_count(16.0, 2.7, 0.53, 10.0, 0, [0.9, 0.16])
    assert r["doors_total_m"] == 1.06
    assert r["effective_perimeter_m"] == 14.94
    assert r["drops"] == 29
    assert r["rolls"] == 10
    # drop_len and strips per roll are unaffected by doors
    assert r["drop_len_m"] == 2.7
    assert r["strips_per_roll"] == 3


def test_non_positive_effective_perimeter_rejected():
    with pytest.raises(ValueError):
        roll_count(16.0, 2.7, 0.53, 10.0, 0, [16.0])
    with pytest.raises(ValueError):
        roll_count(16.0, 2.7, 0.53, 10.0, 0, [20.0])
