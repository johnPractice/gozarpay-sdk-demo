from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional
import time
import requests
from ..exceptions import AuthenticationError


class AuthStrategy(ABC):
    """Auth strategy interface."""

    @abstractmethod
    def attach(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Return headers with auth information, if any."""
        ...

    def on_401_and_retry(self, session: requests.Session) -> bool:
        """Optional: handle 401 once (e.g., refresh). Return True to retry."""
        return False


@dataclass(slots=True)
class NoAuth(AuthStrategy):
    def attach(self, headers: Dict[str, str]) -> Dict[str, str]:
        return headers


@dataclass(slots=True)
class TokenAuth(AuthStrategy):
    base_url: str
    access_token: str
    refresh_token: Optional[str] = None
    access_expires_at: Optional[float] = None

    def attach(self, headers: Dict[str, str]) -> Dict[str, str]:
        if self.access_expires_at and time.time() >= self.access_expires_at - 30:
            # naive TTL; optional improvement: decode JWT exp
            pass
        headers = dict(headers or {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def on_401_and_retry(self, session: requests.Session) -> bool:
        if not self.refresh_token:
            return False
        url = f"{self.base_url.rstrip('/')}/tp/v1/usr/refresh-token/"
        resp = session.post(url, json={"refresh": self.refresh_token})
        if resp.status_code != 200:
            return False
        data = resp.json()
        access = data.get("access")
        if not access:
            return False
        self.access_token = access
        self.access_expires_at = time.time() + 50 * 60
        return True


@dataclass(slots=True)
class ApiKeyAuth(AuthStrategy):
    base_url: str
    api_key: str
    secret_key: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    access_expires_at: Optional[float] = None

    def attach(self, headers: Dict[str, str]) -> Dict[str, str]:
        if not self.access_token:
            self._login()
        if self.access_expires_at and time.time() >= self.access_expires_at - 30:
            self._refresh()
        headers = dict(headers or {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def on_401_and_retry(self, session: requests.Session) -> bool:
        try:
            self._refresh(session=session)
            return True
        except AuthenticationError:
            return False

    def _login(self, session: Optional[requests.Session] = None) -> None:
        s = session or requests.Session()
        url = f"{self.base_url.rstrip('/')}/tp/v1/usr/api-login/"
        resp = s.post(
            url, json={"api_key": self.api_key, "secret_key": self.secret_key}
        )
        if resp.status_code != 200:
            raise AuthenticationError(
                f"Failed API login: {resp.status_code} {resp.text}"
            )
        data = resp.json()
        access = data.get("access_token") or data.get("token")
        refresh = data.get("refresh_token")
        if not access or not refresh:
            raise AuthenticationError("Login response missing access/refresh tokens")
        self.access_token = access
        self.refresh_token = refresh
        self.access_expires_at = time.time() + 50 * 60

    def _refresh(self, session: Optional[requests.Session] = None) -> None:
        if not self.refresh_token:
            raise AuthenticationError("No refresh token present.")
        s = session or requests.Session()
        url = f"{self.base_url.rstrip('/')}/tp/v1/usr/refresh-token/"
        resp = s.post(url, json={"refresh": self.refresh_token})
        if resp.status_code != 200:
            raise AuthenticationError(
                f"Failed to refresh token: {resp.status_code} {resp.text}"
            )
        data = resp.json()
        access = data.get("access")
        if not access:
            raise AuthenticationError("Refresh response missing access token")
        self.access_token = access
        self.access_expires_at = time.time() + 50 * 60
