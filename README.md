Here’s a complete, copy-paste-ready **README.md** for your SDK.

---

# GozarPay Python SDK

Clean, typed client for the GozrPay API (Python **3.11+**) featuring:

* **Pydantic v2** models for safe parsing
* **Auth strategies** (NoAuth / TokenAuth / ApiKeyAuth → tokens)
* **Versioning**: pass `version="v1"` / `version="v2"` (or `ApiVersion.v1/v2`) and routes auto-switch

---

## Requirements

* Python **3.11+**
* `requests>=2.31.0`
* `pydantic>=2.5,<3.0`

---

## Install

```bash
pip install gozarpay
```

Or local editable install for development:

```bash
pip install -e .
```

---

## Quickstart

```python
import gozarpay
from gozarpay import ApiVersion

# Option A — from environment (OpenAI-style)
# Reads: GOZARPAY_BASE_URL, GOZARPAY_API_KEY, GOZARPAY_SECRET_KEY,
#        GOZARPAY_ACCESS_TOKEN, GOZARPAY_REFRESH_TOKEN, GOZARPAY_API_VERSION (optional)
client = gozarpay.from_env()

# Option B — API keys (SDK exchanges for access/refresh tokens)
client = gozarpay.client_with_api_keys(
    base_url="https://api.gozarpay.com",
    api_key="YOUR_API_KEY",
    secret_key="YOUR_SECRET_KEY",
    version=ApiVersion.v1,   # or "v1" / "v2" (default "v1")
)

# Option C — existing tokens (no login call)
client = gozarpay.client_with_tokens(
    base_url="https://api.gozarpay.com",
    access_token="ACCESS",
    refresh_token="REFRESH",
    version="v2",
)

# Public endpoint (no auth header)
prices = client.market.price_stats(code1="BTC", code2="USDT")
for p in prices:
    print(p.code, p.price, p.buy_price, p.sell_price)

# Authenticated endpoints (receipts)
receipt = client.receipt.create(
    irt_amount="1000000.00",
    phone_number="+989121234567",
    reference_id="order-123",
)
print(receipt.id, receipt.status)

# Fetch a receipt
r = client.receipt.get(receipt_id=receipt.id)

# Verify / Refund
client.receipt.verify(reference_id="order-123")
client.receipt.refund(reference_id="order-123")

# Iterate paginated receipts
for r in client.receipt.iter_receipts():
    print(r.id, r.status)

# Wallets by phone
wallets = client.wallet.list_by_phone(phone="+989121234567", search="USDT")
print(wallets.count, len(wallets.results))
```

---

## Versioning

Set the version when creating the client; routes are resolved via a **VersionRouter**:

```python
from gozarpay import ApiVersion, client_public

client_v1 = client_public(base_url="https://api.gozarpay.com", version=ApiVersion.v1)
client_v2 = client_public(base_url="https://api.gozarpay.com", version="v2")  # string is fine too
```

You can also set the env var `GOZARPAY_API_VERSION` (e.g., `v1`, `v2`) and call `gozarpay.from_env()`.

Current versioned routes include:

* `market.price_stats`
* `receipt.create`, `receipt.verify`, `receipt.refund`, `receipt.get`, `receipt.list`
* `wallet.list_by_phone`

> If future API versions add or move endpoints, you only need to update the version routing table—service code stays unchanged.

---

## Environment variables

`from_env()` reads:

* `GOZARPAY_BASE_URL` — e.g., `https://api.gozarpay.com`
* `GOZARPAY_API_KEY`, `GOZARPAY_SECRET_KEY` — optional (login)
* `GOZARPAY_ACCESS_TOKEN`, `GOZARPAY_REFRESH_TOKEN` — optional (direct tokens)
* `GOZARPAY_API_VERSION` — optional (`v1` default)

---

## Package architecture (clean code)

```
src/gozarpay/
├─ __init__.py                  # exports Client, factories, ApiVersion
├─ client.py                    # thin HTTP client; uses strategies & router
├─ exceptions.py                # APIError, AuthenticationError, base error
├─ models.py                    # Pydantic v2 models (typed)
├─ versioning.py                # ApiVersion, VersionSpec, VersionRouter
├─ config.py                    # ClientConfig dataclass
├─ factory.py                   # builders: tokens / api-keys / public + from_env
├─ auth/
│  └─ strategies.py             # NoAuth, TokenAuth, ApiKeyAuth
└─ services/
   ├─ __init__.py               # re-exports
   ├─ market.py                 # market.price_stats (public)
   ├─ receipt.py                # create/verify/refund/get/list/iter
   └─ wallet.py                 # list_by_phone
```

**Why this structure?**

* **Single responsibility** per module.
* **Testable**: strategies and builders can be unit-tested in isolation.
* **Extensible**: add a new auth flow or API version without touching client/service code.
* **Maintainable**: services are grouped logically; versioning is declarative.

---

## Error handling

* `APIError`: raised for non-2xx responses. Includes `status_code`, and parsed `payload` when available.
* `AuthenticationError`: thrown when login/refresh fails or when private endpoints are called without valid auth.

Example:

```python
from gozarpay.exceptions import APIError, AuthenticationError

try:
    receipt = client.receipt.get(receipt_id=123)
except AuthenticationError as e:
    # Handle missing/expired credentials
    ...
except APIError as e:
    print(e.status_code, e.payload)  # inspect server payload
```

---

## Typing & models

All responses parse into **Pydantic v2** models:

* `MarketPrice`, `Receipt`, `PaginatedReceiptList`, `Wallet`, `PaginatedWalletList`, etc.
* Extra fields from the server are ignored for forward-compatibility.
* Enums (e.g., `ReceiptStatus`) are typed for safer logic.

---

## Public vs private endpoints

* **Public**: `market.price_stats` (no auth header attached).
* **Private**: receipts and wallet endpoints require authorization.

  * Use `(api_key, secret_key)` to obtain tokens via the API.
  * Or pass `(access_token, refresh_token)` directly.

The SDK will attempt a **single refresh** on `401` when possible.

---

## Advanced: direct Client (bypassing factory)

You can instantiate `Client` directly with a specific auth strategy (advanced usage):

```python
from gozarpay.client import Client
from gozarpay.auth.strategies import TokenAuth
from gozarpay import ApiVersion

client = Client(
    base_url="https://api.gozarpay.com",
    version=ApiVersion.v2,
    auth_strategy=TokenAuth(
        base_url="https://api.gozarpay.com",
        access_token="ACCESS",
        refresh_token="REFRESH",
    ),
)
```

---

## Contributing

1. Fork & clone
2. Create a virtual environment (Python **3.11**)
3. `pip install -e .`
4. Run / write tests (add your test framework of choice)
5. Open a PR

---

## License
MIT License

---

## Changelog

* **0.1.0** — Initial release.
