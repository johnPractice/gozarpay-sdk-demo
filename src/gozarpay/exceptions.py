from typing import Optional, Any, Dict


class GozarPayError(Exception):
    """Base exception for SDK."""


class AuthenticationError(GozarPayError):
    """Auth handshake or token refresh failed."""


class APIError(GozarPayError):
    """Raised for non-2xx HTTP responses."""

    def __init__(
        self,
        status_code: int,
        message: str,
        *,
        url: Optional[str] = None,
        method: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        detail = f"HTTP {status_code}"
        if method and url:
            detail += f" {method} {url}"
        super().__init__(f"{detail}: {message}")
        self.status_code = status_code
        self.url = url
        self.method = method
        self.payload = payload or {}
        self.headers = headers or {}
