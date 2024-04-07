"""Utils with Enums."""

import enum


class CSRFConstants(str, enum.Enum):
    """Enum based class to set constants for CSRF."""

    CSRF_TOKEN_NAME = "csrftoken"
    CSRF_TOKEN_EXPIRY = 5000


class RatePeriod(str, enum.Enum):
    """Predefined periods for RateLimiters. Used in datetime.timedelta constructor."""

    SECOND = "seconds"
    MINUTE = "minutes"
    HOUR = "hours"
    DAY = "days"
    WEEK = "weeks"
