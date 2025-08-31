from __future__ import annotations
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict, field_validator
import json


class ReceiptStatus(str, Enum):
    initialized = "initialized"
    pending = "pending"
    success = "success"
    failed_insufficient_amount = "failed_insufficient_amount"
    failed_not_verified = "failed_not_verified"
    expired = "expired"
    refunded = "refunded"
    waiting_payment = "waiting_payment"
    refund_failed = "refund_failed"
    divar_verification = "divar_verification"
    divar_verification_notified = "divar_verification_notified"


class Network(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    code: str
    title: str
    title_fa: Optional[str] = None
    image: Optional[str] = None


class Currency(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    code: str
    title_fa: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    color: Optional[str] = None
    networks: List[Network] = []


class CurrencySummery(BaseModel):  # naming follows schema
    model_config = ConfigDict(extra="ignore")
    id: int
    code: str
    title_fa: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    color: Optional[str] = None
    decimal: Optional[int] = None
    decimal_amount: Optional[int] = None
    decimal_irt: Optional[int] = None


class Wallet(BaseModel):
    model_config = ConfigDict(extra="ignore")
    currency: CurrencySummery
    balance: str
    value_total: str


class PaginatedWalletList(BaseModel):
    model_config = ConfigDict(extra="ignore")
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Wallet]


# --- NEW: PriceInfo to match actual response shape ---
class PriceInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")
    created_at: Optional[Union[float, int]] = None
    price: Optional[str] = None
    change: Optional[Union[float, int]] = None
    min: Optional[str] = None
    max: Optional[str] = None
    time: Optional[Union[float, int, str]] = None
    mean: Optional[Union[float, int, str]] = None
    value: Optional[Union[float, int, str]] = None
    amount: Optional[Union[float, int, str]] = None


class MarketPrice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    code: str
    # Accept dict or string; normalize dict/JSON-string to PriceInfo
    price_info: Union[PriceInfo, str]
    price: str
    buy_price: str
    sell_price: str

    @field_validator("price_info", mode="before")
    @classmethod
    def _coerce_price_info(cls, v):
        # If server returned a dict, parse to PriceInfo
        if isinstance(v, dict):
            return PriceInfo.model_validate(v)
        # If server returned a JSON string, try to parse → dict → PriceInfo
        if isinstance(v, str):
            try:
                obj = json.loads(v)
                if isinstance(obj, dict):
                    return PriceInfo.model_validate(obj)
            except Exception:
                # keep as raw string if not JSON
                return v
        # Anything else: let Pydantic validate (will raise if incompatible)
        return v


class ReceiptCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    irt_amount: str
    reference_id: str
    phone_number: str
    callback: str


class VerifyReceipt(BaseModel):
    model_config = ConfigDict(extra="ignore")
    reference_id: str


class Receipt(BaseModel):
    model_config = ConfigDict(extra="ignore")
    redirect_url: str


class PaginatedReceiptList(BaseModel):
    model_config = ConfigDict(extra="ignore")
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Receipt]
