from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


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


class MarketPrice(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    code: str
    price_info: str
    price: str
    buy_price: str
    sell_price: str


class ReceiptCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    irt_amount: str
    reference_id: str
    phone_number: str


class VerifyReceipt(BaseModel):
    model_config = ConfigDict(extra="ignore")
    reference_id: str


class Receipt(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    user_phone: str
    status: ReceiptStatus
    tracking_code: Optional[str] = None
    irt_amount: str
    reference_id: str
    currency: Optional[Currency] = None
    network: Optional[Network] = None
    amount: Optional[str] = None
    paid_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    expire_at: Optional[str] = None


class PaginatedReceiptList(BaseModel):
    model_config = ConfigDict(extra="ignore")
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Receipt]
