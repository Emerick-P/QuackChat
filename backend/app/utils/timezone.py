from datetime import datetime, timezone

def ensure_aware(dt: datetime) -> datetime:
    """
    Ensures that a datetime object is timezone-aware (UTC).
    If the datetime is naive, assigns UTC timezone.

    Args:
        dt (datetime): The datetime object to check.

    Returns:
        datetime: A timezone-aware datetime (UTC).
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt