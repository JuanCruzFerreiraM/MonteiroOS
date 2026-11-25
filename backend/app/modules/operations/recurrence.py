"""Deterministic expansion of a schedule revision.

An occurrence belongs to the calendar day on which its interval starts, in
America/Argentina/Buenos_Aires. When the end clock time is earlier than the
start, the interval finishes on the next calendar day. Equal times are not a
zero-length interval and are rejected.
"""

from datetime import date, datetime, time, timedelta

from app.modules.operations.clock import APP_TIMEZONE, CLOCK_TOLERANCE
from app.modules.production.rules import DomainError

MAX_RANGE_DAYS = 62


def normalize_weekdays(value: object) -> list[int]:
    if not isinstance(value, list) or not value:
        raise DomainError(422, "Seleccione al menos un día de la semana.")
    days: list[int] = []
    for item in value:
        if isinstance(item, bool) or not isinstance(item, int):
            raise DomainError(
                422,
                "El día de la semana debe estar entre 1 (lunes) y 7 (domingo).",
            )
        if item < 1 or item > 7:
            raise DomainError(
                422,
                "El día de la semana debe estar entre 1 (lunes) y 7 (domingo).",
            )
        if item in days:
            raise DomainError(422, "Los días de la semana no pueden repetirse.")
        days.append(item)
    return sorted(days)


def normalize_clock(value: object, label: str) -> time:
    if isinstance(value, datetime):
        raise DomainError(422, f"La {label} es una hora del día, sin fecha.")
    if isinstance(value, time):
        parsed = value
    elif isinstance(value, str):
        raw = value.strip()
        try:
            parsed = time.fromisoformat(raw)
        except ValueError:
            raise DomainError(
                422,
                f"La {label} debe ser una hora válida (HH:MM).",
            ) from None
    else:
        raise DomainError(422, f"La {label} debe ser una hora válida (HH:MM).")
    if parsed.tzinfo is not None:
        raise DomainError(
            422,
            f"La {label} es una hora civil, sin zona horaria.",
        )
    return parsed.replace(microsecond=0)


def require_period(start: date, end: date) -> None:
    if end < start:
        raise DomainError(422, "La fecha de fin no puede ser anterior al inicio.")


def require_distinct_times(start: time, end: time) -> None:
    if start == end:
        raise DomainError(
            422,
            "El inicio y el fin programados no pueden ser iguales.",
        )


def require_range(start: date, end: date) -> None:
    if end < start:
        raise DomainError(422, "La fecha de fin es anterior a la de inicio.")
    if (end - start).days > MAX_RANGE_DAYS - 1:
        raise DomainError(
            422,
            "El período consultado no puede superar 62 días.",
        )


def expected_bounds(day: date, start: time, end: time) -> tuple[datetime, datetime]:
    start_at = datetime.combine(day, start, APP_TIMEZONE)
    end_day = day + timedelta(days=1) if end < start else day
    end_at = datetime.combine(end_day, end, APP_TIMEZONE)
    return start_at, end_at


def iter_dates(start: date, end: date, weekdays: list[int]):
    selected = set(weekdays)
    day = start
    while day <= end:
        if day.isoweekday() in selected:
            yield day
        day += timedelta(days=1)


def window_has_ended(end_at: datetime, now: datetime) -> bool:
    return end_at <= now + CLOCK_TOLERANCE
