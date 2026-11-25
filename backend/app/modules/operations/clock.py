from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from app.modules.production.rules import DomainError

APP_TIMEZONE = ZoneInfo("America/Argentina/Buenos_Aires")
CLOCK_TOLERANCE = timedelta(minutes=5)


def utc_now() -> datetime:
    return datetime.now(UTC)


def local_today(now: datetime | None = None):
    current = now or utc_now()
    return current.astimezone(APP_TIMEZONE).date()


def ensure_aware(value: datetime, label: str) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise DomainError(422, f"La {label} debe incluir una zona horaria.")
    return value.astimezone(UTC)


def reject_future(value: datetime, label: str, *, now: datetime | None = None) -> None:
    """Reject a timestamp more than five minutes ahead of the server clock.

    The tolerance covers ordinary clock skew. It is not a grace period for
    planning future work. The database does not enforce it: a check against
    ``now()`` would make a valid row fail the next day.
    """
    current = now or utc_now()
    if value > current + CLOCK_TOLERANCE:
        raise DomainError(422, f"La {label} no puede estar en el futuro.")
