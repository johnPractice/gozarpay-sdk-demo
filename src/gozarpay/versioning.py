from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict


class ApiVersion(str, Enum):
    v1 = "v1"
    v2 = "v2"


@dataclass(frozen=True, slots=True)
class VersionSpec:
    """Routing table for a given API version."""

    name: str
    routes: Dict[str, str]  # e.g. "receipt.create" -> "/tp/v1/rpt/divar/create/"


# v1 routes (from provided Swagger)
V1_SPEC = VersionSpec(
    name="v1",
    routes={
        # market
        "market.price_stats": "/tp/v1/mrt/markets/price-stats/",
        # receipts
        "receipt.create": "/tp/v1/rpt/divar/create/",
        "receipt.verify": "/tp/v1/rpt/divar/verify/",
        "receipt.refund": "/tp/v1/rpt/divar/refund/",
        "receipt.get": "/tp/v1/rpt/receipts/{id}/",
        "receipt.list": "/tp/v1/rpt/receipts/",
        # wallets
        "wallet.list_by_phone": "/tp/v1/wlt/wallets/{phone}/",
    },
)

# v2 routes (default: same keys, replace /v1/ with /v2/)
V2_SPEC = VersionSpec(
    name="v2",
    routes={key: path.replace("/v1/", "/v2/") for key, path in V1_SPEC.routes.items()},
)

SPECS: Dict[ApiVersion, VersionSpec] = {
    ApiVersion.v1: V1_SPEC,
    ApiVersion.v2: V2_SPEC,
}


class VersionRouter:
    """Resolves route keys to versioned paths."""

    def __init__(self, spec: VersionSpec) -> None:
        self.spec = spec

    def path(self, key: str, **fmt) -> str:
        pattern = self.spec.routes.get(key)
        if pattern is None:
            raise KeyError(f"Route '{key}' not defined for version '{self.spec.name}'.")
        return pattern.format(**fmt)
