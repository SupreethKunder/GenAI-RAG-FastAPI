"""Utils with Enums."""

import enum


class SSEConstants(str, enum.Enum):
    """Enum based class to set constants for SSE."""

    STREAM_DELAY = 3
    RETRY_TIMEOUT = 5000


class RatePeriod(str, enum.Enum):
    """Predefined periods for RateLimiters. Used in datetime.timedelta constructor."""

    SECOND = "seconds"
    MINUTE = "minutes"
    HOUR = "hours"
    DAY = "days"
    WEEK = "weeks"
