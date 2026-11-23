"""
providers package

Provider-agnostic seam for vision-based diagram extraction. Register one
adapter per vendor; the rest of the app selects a provider by id and never
depends on a vendor SDK directly.

See ``providers/base.py`` for the interface.
"""

from __future__ import annotations

from typing import Dict, List

from providers.anthropic_provider import AnthropicProvider
from providers.base import (
    BaseVisionProvider,
    ErrorHelp,
    ModelInfo,
    ProviderError,
    ProviderSpec,
    VisionResponse,
    classify_provider_error,
    image_to_base64,
    resolve_api_key,
    sdk_installed,
)
from providers.gemini_provider import GeminiProvider
from providers.openai_provider import OpenAIProvider

# Order here is the order shown in provider pickers.
_PROVIDERS: Dict[str, BaseVisionProvider] = {
    GeminiProvider.spec.id: GeminiProvider(),
    OpenAIProvider.spec.id: OpenAIProvider(),
    AnthropicProvider.spec.id: AnthropicProvider(),
}


def provider_ids() -> List[str]:
    """Return registered provider ids in display order."""
    return list(_PROVIDERS.keys())


def all_specs() -> List[ProviderSpec]:
    """Return every registered provider's :class:`ProviderSpec`."""
    return [p.spec for p in _PROVIDERS.values()]


def get_provider(provider_id: str) -> BaseVisionProvider:
    """Return the provider adapter for *provider_id*.

    Args:
        provider_id: A registered provider id.

    Returns:
        The provider instance.

    Raises:
        ProviderError: If no provider is registered under that id.
    """
    try:
        return _PROVIDERS[provider_id]
    except KeyError as exc:
        raise ProviderError(f"Unknown provider: {provider_id!r}") from exc


def get_spec(provider_id: str) -> ProviderSpec:
    """Return the :class:`ProviderSpec` for *provider_id*."""
    return get_provider(provider_id).spec


__all__ = [
    "BaseVisionProvider",
    "ErrorHelp",
    "ModelInfo",
    "ProviderError",
    "ProviderSpec",
    "VisionResponse",
    "classify_provider_error",
    "image_to_base64",
    "resolve_api_key",
    "sdk_installed",
    "provider_ids",
    "all_specs",
    "get_provider",
    "get_spec",
]
