from datetime import date

from app.modules.production.rules import cycle_status, periods_overlap


def test_status_follows_the_end_date() -> None:
    assert cycle_status(None) == "active"
    assert cycle_status(date(2024, 3, 1)) == "finalized"


def test_inclusive_ranges_overlap_on_a_shared_day_and_not_on_the_next() -> None:
    planting = date(2024, 1, 1)
    closing = date(2024, 3, 1)
    same_day = date(2024, 3, 1)
    next_day = date(2024, 3, 2)

    assert periods_overlap(planting, closing, same_day, date(2024, 4, 1))
    assert not periods_overlap(planting, closing, next_day, date(2024, 4, 1))


def test_an_open_cycle_overlaps_any_later_period() -> None:
    assert periods_overlap(
        date(2024, 1, 1),
        None,
        date(2024, 6, 1),
        date(2024, 8, 1),
    )
    assert not periods_overlap(
        date(2024, 1, 1),
        date(2024, 3, 1),
        date(2024, 3, 2),
        None,
    )


def test_a_one_day_cycle_occupies_that_calendar_day() -> None:
    day = date(2024, 5, 10)
    assert periods_overlap(day, day, day, day)
    assert not periods_overlap(day, day, date(2024, 5, 11), date(2024, 5, 11))
