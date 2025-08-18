from __future__ import annotations
from typing import Any, Dict, Optional
from ..models import PaginatedWalletList
from ..versioning import VersionRouter


class WalletService:
    def __init__(self, request, router: VersionRouter):
        self._request = request
        self._router = router

    def list_by_phone(
        self, *, phone: str, page: Optional[int] = None, search: Optional[str] = None
    ) -> PaginatedWalletList:
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if search is not None:
            params["search"] = search
        path = self._router.path("wallet.list_by_phone", phone=phone)
        resp = self._request("GET", path, params=params)
        return PaginatedWalletList.model_validate(resp.json())
