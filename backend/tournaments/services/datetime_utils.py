from __future__ import annotations

from datetime import datetime, timezone as dt_timezone

from django.utils import timezone


def ensure_aware_datetime(value: datetime) -> datetime:
    """Normalize datetimes to timezone-aware UTC."""
    if timezone.is_aware(value):
        return value
    return timezone.make_aware(value, dt_timezone.utc)
