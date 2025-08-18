from __future__ import annotations
from typing import Iterator, Optional
from ..models import Receipt, VerifyReceipt, ReceiptCreate, PaginatedReceiptList
from ..versioning import VersionRouter


class ReceiptService:
    def __init__(self, request, router: VersionRouter):
        self._request = request
        self._router = router

    def create(
        self, *, irt_amount: str, reference_id: str, phone_number: str
    ) -> Receipt:
        payload = ReceiptCreate(
            irt_amount=irt_amount, reference_id=reference_id, phone_number=phone_number
        ).model_dump()
        path = self._router.path("receipt.create")
        resp = self._request("POST", path, json=payload)
        return Receipt.model_validate(resp.json())

    def verify(self, *, reference_id: str) -> VerifyReceipt:
        path = self._router.path("receipt.verify")
        resp = self._request(
            "POST", path, json=VerifyReceipt(reference_id=reference_id).model_dump()
        )
        return VerifyReceipt.model_validate(resp.json())

    def refund(self, *, reference_id: str) -> VerifyReceipt:
        path = self._router.path("receipt.refund")
        resp = self._request(
            "POST", path, json=VerifyReceipt(reference_id=reference_id).model_dump()
        )
        return VerifyReceipt.model_validate(resp.json())

    def get(self, *, receipt_id: int) -> Receipt:
        path = self._router.path("receipt.get", id=receipt_id)
        resp = self._request("GET", path)
        return Receipt.model_validate(resp.json())

    def list(self, *, page: Optional[int] = None) -> PaginatedReceiptList:
        params = {"page": page} if page is not None else {}
        path = self._router.path("receipt.list")
        resp = self._request("GET", path, params=params)
        return PaginatedReceiptList.model_validate(resp.json())

    def iter_receipts(self) -> Iterator[Receipt]:
        page: Optional[int] = 1
        while True:
            pg = self.list(page=page)
            for item in pg.results:
                yield item
            if not pg.next:
                break
            page = (page or 1) + 1
