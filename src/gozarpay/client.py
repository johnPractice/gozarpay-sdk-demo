from __future__ import annotations
from typing import Any, Dict, Optional, Callable
import requests
from .exceptions import APIError
from .auth.strategies import AuthStrategy, NoAuth
from .services import MarketService, ReceiptService, WalletService
from .versioning import ApiVersion, SPECS, VersionRouter

DEFAULT_TIMEOUT = 30


class Client:
    """
    High-level API client (no if/elif branching here).
    - Auth is injected via an AuthStrategy (factory decides).
    - Versioned paths are resolved via VersionRouter.
    - Services live in separate modules/files.
    """

    def __init__(
        self,
        *,
        base_url: str,
        version: ApiVersion | str = ApiVersion.v1,
        auth_strategy: Optional[AuthStrategy] = None,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not base_url:
            raise ValueError("base_url is required (e.g., 'https://api.gozarpay.com')")
        self.base_url = base_url.rstrip("/")
        self.version = (
            ApiVersion(version) if not isinstance(version, ApiVersion) else version
        )

        self._session = session or requests.Session()
        self._auth: AuthStrategy = auth_strategy or NoAuth()

        # Version router
        self._router = VersionRouter(SPECS[self.version])

        # Bind a tiny request function for services
        self._request: Callable[..., requests.Response] = self._build_request_fn()

        # Services (receive request callable + router)
        self.market = MarketService(self._request, self._router)
        self.receipt = ReceiptService(self._request, self._router)
        self.wallet = WalletService(self._request, self._router)

    def _build_request_fn(self) -> Callable[..., requests.Response]:
        def _request(
            method: str, path: str, *, auth: bool = True, **kwargs
        ) -> requests.Response:
            url = f"{self.base_url}{path}"
            headers: Dict[str, str] = dict(kwargs.pop("headers", {}) or {})
            if auth:
                headers = self._auth.attach(headers)

            resp = self._session.request(
                method, url, headers=headers, timeout=DEFAULT_TIMEOUT, **kwargs
            )

            # One retry on 401 if strategy supports it
            if resp.status_code == 401 and auth:
                if self._auth.on_401_and_retry(self._session):
                    headers = self._auth.attach(dict(kwargs.get("headers") or {}))
                    resp = self._session.request(
                        method, url, headers=headers, timeout=DEFAULT_TIMEOUT, **kwargs
                    )

            if not (200 <= resp.status_code < 300):
                raise APIError(
                    resp.status_code,
                    "Request failed",
                    url=url,
                    method=method,
                    payload=_safe_json(resp),
                )
            return resp

        return _request


def _safe_json(resp: requests.Response) -> Dict[str, Any]:
    try:
        return resp.json()
    except Exception:
        return {"text": resp.text}


# Developer-friendly alias
GozarPayClient = Client
