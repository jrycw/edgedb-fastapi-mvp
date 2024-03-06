import datetime


def _ensure_nice_datetime(d: datetime.datetime | str) -> datetime.datetime:
    if isinstance(d, str):
        # `Z` is coming from EdgeDB
        # datetime.datetime.fromisoformat(d).isoformat() will fail in 3.10
        if d[-1] == "Z":
            d = d[:-1] + "+00:00"
        d: datetime.datetime = datetime.datetime.fromisoformat(d)
    return d


def assert_datetime_equal(
    d1: datetime.datetime | str, d2: datetime.datetime | str
) -> bool:
    assert _ensure_nice_datetime(d1) == _ensure_nice_datetime(d2)
