from __future__ import annotations
from dataclasses import dataclass
from .versioning import ApiVersion


@dataclass(slots=True)
class ClientConfig:
    """
    Configuration for building a client via the factory.
    Provide exactly one auth mode (keys OR tokens) or none for public.
    """

    base_url: str
    version: ApiVersion | str = ApiVersion.v1

    # API keys (SDK exchanges for tokens)
    api_key: str | None = None
    secret_key: str | None = None

    # Pre-acquired tokens
    access_token: str | None = None
    refresh_token: str | None = None
