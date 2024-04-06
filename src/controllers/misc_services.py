import abc
import functools
import typing
import zoneinfo
import pendulum
from fastapi import Depends, Request, Response
from ..core.enums import RatePeriod
from redis import Redis
from ..database.connect import redis_client
from datetime import datetime, timedelta
from ..core.exceptions import BackendError
from fastapi import status as http_status

# This Sliding Window functionality was referred from this link.
# Link: https://github.com/Kostiantyn-Salnykov/fastapi_quickstart/blob/main/apps/CORE/deps/limiters.py


class Rate:
    """Value for RatePeriod.

    Examples:
        >>> str(Rate(number=10, period=RatePeriod.DAY))
        '10 per day'
    """

    def __init__(self, number: int, period: RatePeriod) -> None:
        self._number = number
        self._period = period

    def __repr__(self) -> str:
        """Representation for Rate."""
        return (
            f'{self.__class__.__name__}(number={self.number}, period="{self.period}")'
        )

    def __str__(self) -> str:
        """Human representation for Rate."""
        return f"{self.number} per {self.period.value.removesuffix('s')}"

    @property
    def number(self) -> int:
        """Returns value for periods from Rate."""
        return self._number

    @property
    def period(self) -> RatePeriod:
        """Returns period from Rate."""
        return self._period

    @functools.cached_property
    def window_period(
        self,
    ) -> typing.Literal["second", "minute", "hour", "day", "week"]:
        match self.period:
            case RatePeriod.SECOND:
                return "second"
            case RatePeriod.MINUTE:
                return "minute"
            case RatePeriod.HOUR:
                return "hour"
            case RatePeriod.DAY:
                return "day"
            case RatePeriod.WEEK:
                return "week"

    @functools.cached_property
    def seconds(self) -> int:
        match self.period:
            case RatePeriod.SECOND:
                return 1
            case RatePeriod.MINUTE:
                return 60
            case RatePeriod.HOUR:
                return 60 * 60
            case RatePeriod.DAY:
                return 60 * 60 * 24
            case RatePeriod.WEEK:
                return 60 * 60 * 24 * 7

    @functools.cached_property
    def milliseconds(self) -> int:
        return self.seconds * 1000

    @functools.cached_property
    def headers(self) -> dict[str, str]:
        return {
            "RateLimit-Limit": f"{self.number}",
            "RateLimit-Policy": f"{self.number};w={self.seconds}",
        }


class BaseRedisRateLimiter(abc.ABC):
    """Base realization for limiter, adapted to Redis."""

    def __init__(self, rate: Rate, key_prefix: str = "limiter") -> None:
        self._rate = rate
        self._key_prefix = key_prefix

    @abc.abstractmethod
    async def __call__(
        self,
        *,
        request: Request,
        response: Response,
        redis_client: Redis = Depends(redis_client),
    ) -> None:
        raise NotImplementedError

    @property
    def rate(self) -> Rate:
        """Return limiter's Rate."""
        return self._rate

    @property
    def key_prefix(self) -> str:
        """Return limiter's key prefix."""
        return self._key_prefix

    def key(
        self, *, request: Request, now: pendulum.DateTime, previous: bool = False
    ) -> str:
        """Construct key for Redis.

        Examples:
            key="limiter:/api/v1/login/:127.0.0.1:2023-03-12T13:32:00+00:00:minute:5"

        Keyword Args:
            request (Request): FastAPI Request instance.
            now (pendulum.DateTime): DateTime instance from pendulum package.
            previous (bool): Select previous windows instead of current.

        Returns:
            (str): Unique key for Redis
        """
        window_ts = (
            int(self.previous_window_start(now=now).timestamp())
            if previous
            else int(self.current_window_start(now=now).timestamp())
        )
        return (
            f"{self.key_prefix}:{request.url.path}:{self.get_ip(request=request)}:"
            f"{window_ts}:{self.rate.window_period}:{self.rate.number}"
        )

    @staticmethod
    def get_ip(request: Request) -> str:
        """Retrieve client IP (in case if requester not authenticated)."""
        try:
            ip_address = request.headers["X-Real-IP"]
        except Exception:
            ip_address = request.client.host
        return ip_address

    def now(self) -> pendulum.DateTime:
        """Returns current datetime with timezone, via pendulum library."""
        default_datetime_now = datetime.now(tz=zoneinfo.ZoneInfo(key="UTC"))
        return pendulum.from_timestamp(
            timestamp=default_datetime_now.timestamp(), tz=default_datetime_now.tzinfo
        )

    def previous_window_start(self, now: pendulum.DateTime) -> pendulum.DateTime:
        """Calculates the previous window."""
        return self.current_window_start(now=now) - timedelta(seconds=self.rate.seconds)

    def current_window_start(self, now: pendulum.DateTime) -> pendulum.DateTime:
        """Calculates the current window."""
        return now.start_of(unit=self.rate.window_period)

    def next_window_start(self, now: pendulum.DateTime) -> pendulum.DateTime:
        """Calculates the next window."""
        return self.current_window_start(now=now) + timedelta(seconds=self.rate.seconds)

    def expiration(self, now: pendulum.DateTime) -> pendulum.Duration:
        """Calculate expiration for the key."""
        return self.next_window_start(now=now) - now


class SlidingWindowRateLimiter(BaseRedisRateLimiter):
    async def __call__(
        self,
        request: Request,
        response: Response,
    ) -> None:
        now = self.now()
        key = self.key(request=request, now=now)
        print(key)
        # === Redis logic starts ===
        count = int(redis_client.get(name=key) or 0)
        if int(count) >= self.rate.number:
            rate_limit_headers = self.get_and_update_headers(
                request=request, response=response, hits=count
            )
            raise BackendError(
                message=f"Request limit exceeded for this quota: '{self.rate}'.",
                headers=rate_limit_headers,
                code=http_status.HTTP_429_TOO_MANY_REQUESTS,
            )

        prev_key = self.key(request=request, now=now, previous=True)
        prev_count = int(redis_client.get(name=prev_key) or 0)
        prev_percentage = (now.timestamp() % self.rate.seconds) / self.rate.seconds
        weight_count = prev_count * (1 - prev_percentage) + count

        rate_limit_headers = self.get_and_update_headers(
            request=request,
            response=response,
            hits=count,
            weight_count=weight_count,
        )
        if weight_count >= self.rate.number:
            raise BackendError(
                message=f"Request limit exceeded for this quota, overloaded {weight_count:0.3f}/{self.rate.number} for the latest window ({self.rate.window_period}).",
                headers=rate_limit_headers,
                code=http_status.HTTP_429_TOO_MANY_REQUESTS,
            )

        expiration = (
            self.current_window_start(now=now)
            + timedelta(seconds=self.rate.seconds * 2)
        ) - now
        pipe = redis_client.pipeline(transaction=False)
        pipe.incr(name=key)
        pipe.expire(name=key, time=expiration.seconds)
        pipe.execute()
        return rate_limit_headers
        # === Redis Logic ends ===

    def get_and_update_headers(
        self,
        *,
        request: Request,
        response: Response,
        hits: int,
        weight_count: float | None = None,
    ) -> dict[str, str]:
        if weight_count is not None:
            remaining = int(self.rate.number - weight_count)
            rate_limit_remaining = {
                "RateLimit-Remaining": f'{remaining};comment="flood weight={weight_count:0.3f}/{self.rate.number}"',
            }
        else:
            remaining = val if (val := self.rate.number - hits - 1) >= 0 else 0
            rate_limit_remaining = {
                "RateLimit-Remaining": f'{remaining};comment="exceeded quota by count."'
            }

        result_headers = (
            self.rate.headers
            | {
                "RateLimit-Policy": f'{self.rate.number};w={self.rate.seconds};comment="sliding window"',
                "Location": request.url.path,
            }
            | rate_limit_remaining
        )

        response.headers.update(result_headers)
        # print(response.headers)
        return result_headers
