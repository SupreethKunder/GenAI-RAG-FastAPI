import typing

from fastapi import status as http_status


class BackendError(Exception):
    """Exception for Back-end with JSONResponse.

    Examples:
        >>> raise BackendError(
        ...     status='success',
        ...     data=["Something", "Interesting"],
        ...     message="Fascinating exception.",
        ...     code=http_status.HTTP_200_OK, headers = {}
        ... )
    """

    def __init__(
        self,
        *,
        status: str = "failure",
        data: None | int | str | list[typing.Any] | dict[str, typing.Any] = None,
        message: str,
        code: int = http_status.HTTP_400_BAD_REQUEST,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Initializer for BackException.

        Keyword Args:
            status (str): status for JsonResponse
            data: any detail or data for this exception.
            message (str): any text detail for this exception.
            code (int): HTTP status code or custom code from Back-end.
        """
        self.status = status
        self.data = data
        self.message = message
        self.code = code
        self.headers = headers

    def __repr__(self) -> str:
        """Representation for BackendException."""
        return (
            f'{self.__class__.__name__}(status={self.status}, data={self.data}, message="{self.message}", '
            f"code={self.code})"
        )

    def __str__(self) -> str:
        """String representation for BackendException."""
        return self.__repr__()

    def dict(self) -> dict[str, typing.Any]:
        """Converts BackendException to python dict. Actually used to wrap JsonResponse."""
        return {
            "status": self.status.value
            if isinstance(self.status, str)
            else self.status,
            "data": self.data,
            "message": self.message,
            "code": self.code,
            "headers": self.headers,
        }
