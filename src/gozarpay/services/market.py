from __future__ import annotations
from typing import Any, Dict, List, Optional
from ..models import MarketPrice
from ..versioning import VersionRouter


class MarketService:
    def __init__(self, request, router: VersionRouter):
        # `request` is a callable injected by Client to perform HTTP calls.
        self._request = request
        self._router = router

    def price_stats(
        self,
        *,
        code1: Optional[str] = None,
        code2: Optional[str] = None,
        currency1: Optional[int] = None,
        currency2: Optional[int] = None,
        title: Optional[str] = None,
        tradable: Optional[bool] = None,
    ) -> List[MarketPrice]:
        """Public endpoint: market price stats (no auth header)."""
        params: Dict[str, Any] = {}
        if code1 is not None:
            params["code1"] = code1
        if code2 is not None:
            params["code2"] = code2
        if currency1 is not None:
            params["currency1"] = currency1
        if currency2 is not None:
            params["currency2"] = currency2
        if title is not None:
            params["title"] = title
        if tradable is not None:
            params["tradable"] = str(tradable).lower()

        path = self._router.path("market.price_stats")
        resp = self._request("GET", path, params=params, auth=False)
        data = resp.json()
        return [MarketPrice.model_validate(item) for item in data]
