"""Timezone helpers.

``datetime.utcnow()`` is deprecated as of Python 3.12 and scheduled for
removal in a future release, because it returns a *naive* datetime (no
``tzinfo``) that silently represents UTC — a common source of bugs when it's
mixed with timezone-aware values. The rest of this codebase (existing
``DateTime`` columns, comparisons, JWT ``exp``/``iat`` claims, etc.) was
written assuming ``utcnow()``'s naive-UTC behavior throughout, so switching
individual call sites to timezone-*aware* datetimes one at a time risks
``TypeError: can't compare offset-naive and offset-aware datetimes`` wherever
an aware value meets a naive one.

``utc_now()`` is a drop-in replacement: it returns the exact same kind of
value ``datetime.utcnow()`` did (naive, UTC), just without calling the
deprecated API. Use it everywhere ``datetime.utcnow()`` used to be called.
"""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return the current UTC time as a naive ``datetime`` (no ``tzinfo``).

    Behaviorally identical to the deprecated ``datetime.utcnow()``.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
