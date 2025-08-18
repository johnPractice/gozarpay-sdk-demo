from __future__ import annotations
import os
from typing import Iterable, Optional, Protocol
from .client import Client
from .config import ClientConfig
from .auth.strategies import ApiKeyAuth, TokenAuth, NoAuth
from .versioning import ApiVersion


# ---- Builder protocol & concrete builders ----


class ClientBuilder(Protocol):
    def can_build(self, cfg: ClientConfig) -> bool: ...
    def build(self, cfg: ClientConfig) -> Client: ...


class TokensBuilder:
    def can_build(self, cfg: ClientConfig) -> bool:
        return bool(cfg.access_token and cfg.refresh_token)

    def build(self, cfg: ClientConfig) -> Client:
        return Client(
            base_url=cfg.base_url,
            version=cfg.version,
            auth_strategy=TokenAuth(cfg.base_url, cfg.access_token, cfg.refresh_token),
        )


class ApiKeysBuilder:
    def can_build(self, cfg: ClientConfig) -> bool:
        return bool(cfg.api_key and cfg.secret_key)

    def build(self, cfg: ClientConfig) -> Client:
        return Client(
            base_url=cfg.base_url,
            version=cfg.version,
            auth_strategy=ApiKeyAuth(cfg.base_url, cfg.api_key, cfg.secret_key),
        )


class PublicBuilder:
    def can_build(self, cfg: ClientConfig) -> bool:
        # Always true as fallback (no auth)
        return True

    def build(self, cfg: ClientConfig) -> Client:
        return Client(
            base_url=cfg.base_url, version=cfg.version, auth_strategy=NoAuth()
        )


_BUILDERS: tuple[ClientBuilder, ...] = (
    TokensBuilder(),
    ApiKeysBuilder(),
    PublicBuilder(),
)


def create_client(
    cfg: ClientConfig, builders: Iterable[ClientBuilder] = _BUILDERS
) -> Client:
    """Decide how to build the client with a builder chain (no if/elif inside Client)."""
    for b in builders:
        if b.can_build(cfg):
            return b.build(cfg)
    raise ValueError("No suitable client builder found.")


# ---- Friendly shortcuts ----


def client_with_tokens(
    *,
    base_url: str,
    access_token: str,
    refresh_token: str,
    version: ApiVersion | str = ApiVersion.v1,
) -> Client:
    return create_client(
        ClientConfig(
            base_url=base_url,
            access_token=access_token,
            refresh_token=refresh_token,
            version=version,
        )
    )


def client_with_api_keys(
    *,
    base_url: str,
    api_key: str,
    secret_key: str,
    version: ApiVersion | str = ApiVersion.v1,
) -> Client:
    return create_client(
        ClientConfig(
            base_url=base_url, api_key=api_key, secret_key=secret_key, version=version
        )
    )


def client_public(
    *, base_url: str, version: ApiVersion | str = ApiVersion.v1
) -> Client:
    return create_client(ClientConfig(base_url=base_url, version=version))


def from_env(
    *, base_url: Optional[str] = None, version: ApiVersion | str = ApiVersion.v1
) -> Client:
    """OpenAI-style factory using env vars; selection is delegated to the builders."""
    base = (base_url or os.getenv("GOZARPAY_BASE_URL") or "").strip()
    ver = os.getenv("GOZARPAY_API_VERSION") or version
    return create_client(
        ClientConfig(
            base_url=base,
            api_key=os.getenv("GOZARPAY_API_KEY"),
            secret_key=os.getenv("GOZARPAY_SECRET_KEY"),
            access_token=os.getenv("GOZARPAY_ACCESS_TOKEN"),
            refresh_token=os.getenv("GOZARPAY_REFRESH_TOKEN"),
            version=ver,
        )
    )
