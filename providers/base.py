"""
providers/base.py

Provider-agnostic seam for vision-based diagram extraction.

A *vision provider* is a thin adapter around one vendor's multimodal API.
Its only job is the raw call: given a model id, an image path and a fully
built text prompt, return the model's raw text response plus a token count.
Prompt construction and schema validation live in the (provider-neutral)
extraction worker, so swapping vendors never touches that logic.

API keys are resolved by *environment variable name*. Each provider has a
default name (``GOOGLE_API_KEY`` etc.), but the name is configurable so a
user can point the app at a key dedicated to PictoSync + that provider
(e.g. ``PICTOSYNC_GEMINI_KEY``).
"""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class ProviderError(RuntimeError):
    """Raised for provider-level failures (missing SDK, bad key, API error)."""


@dataclass
class VisionResponse:
    """Result of a single vision call.

    Attributes:
        text: The model's raw text response (expected to contain JSON).
        tokens: Total tokens billed for the call, or 0 if unavailable.
        stop_reason: Vendor stop/finish reason, normalized where possible
            (e.g. "max_tokens", "stop", "refusal"), or "" if unknown.
        truncated: True when generation stopped because the output token
            limit was hit (the text is very likely incomplete).
    """
    text: str
    tokens: int = 0
    stop_reason: str = ""
    truncated: bool = False


@dataclass
class ModelInfo:
    """One model advertised by a provider's list endpoint.

    Attributes:
        name: The model id to pass when calling the API.
        display: Human-friendly label (falls back to ``name``).
        detail: Optional capability/limit note for display.
    """
    name: str
    display: str = ""
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.display:
            self.display = self.name


@dataclass
class ProviderSpec:
    """Static description of a provider.

    Attributes:
        id: Stable short id (``gemini`` / ``openai`` / ``anthropic``).
        label: Human-friendly vendor name.
        default_env_key: Default environment variable holding the API key.
        install_hint: pip command to install the missing SDK.
        models_doc_url: Where the user can read about models/pricing.
        starter_models: A few known vision model ids to seed the UI.
        pip_package: The pip distribution name to install the SDK.
        import_module: Importable module used to detect the SDK.
        api_keys_url: Vendor page where the user creates/manages API keys.
        billing_url: Vendor page where the user adds credits / sets up billing.
    """
    id: str
    label: str
    default_env_key: str
    install_hint: str
    models_doc_url: str
    starter_models: List[str] = field(default_factory=list)
    pip_package: str = ""
    import_module: str = ""
    api_keys_url: str = ""
    billing_url: str = ""


def sdk_installed(spec: "ProviderSpec") -> bool:
    """Return True if the provider's SDK module can be imported.

    Args:
        spec: The provider spec whose ``import_module`` is checked.

    Returns:
        True when the module is importable in the current interpreter.
    """
    import importlib.util
    mod = (spec.import_module or "").strip()
    if not mod:
        return True
    try:
        return importlib.util.find_spec(mod) is not None
    except (ImportError, ValueError):
        return False


def resolve_api_key(env_key: str) -> str:
    """Return the API key stored in the named environment variable.

    Args:
        env_key: Name of the environment variable to read.

    Returns:
        The key value (stripped), or an empty string if unset.
    """
    return os.environ.get((env_key or "").strip(), "").strip()


def image_to_base64(image_path: str) -> tuple[str, str]:
    """Read an image file and return ``(base64_data, media_type)``.

    Args:
        image_path: Path to the image on disk.

    Returns:
        A tuple of the base64-encoded bytes (ASCII str) and the MIME type.
    """
    ext = Path(image_path).suffix.lower()
    media = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(ext, "image/png")
    with open(image_path, "rb") as fh:
        data = base64.b64encode(fh.read()).decode("ascii")
    return data, media


@dataclass
class ErrorHelp:
    """Actionable interpretation of a provider error.

    Attributes:
        kind: One of ``billing`` / ``auth`` / ``rate_limit`` / ``not_found`` /
            ``network`` / ``unknown``.
        title: Short human-facing headline.
        detail: One or two sentences of plain-language guidance.
        action_url: The most useful page to open (billing, keys, …), or "".
        action_label: Button label for ``action_url``.
    """
    kind: str
    title: str
    detail: str
    action_url: str = ""
    action_label: str = ""


def classify_provider_error(spec: "ProviderSpec", text: str) -> ErrorHelp:
    """Interpret a provider error string into actionable guidance.

    Works on the error *text* (message or traceback) so it is usable even when
    the original exception object is no longer available (e.g. after a worker
    thread has stringified it).

    Args:
        spec: The provider the error came from.
        text: The error message / traceback text.

    Returns:
        An :class:`ErrorHelp` describing what went wrong and what to do.
    """
    t = (text or "").lower()
    label = spec.label

    def has(*needles: str) -> bool:
        return any(n in t for n in needles)

    # Wrong modality: the chosen model can't accept image input at all.
    modality_markers = (
        "modality", "image input", "does not support image",
        "image is not supported", "no image", "not multimodal",
        "input modality",
    )
    # Billing / out-of-credits / quota exhausted. Key is valid; balance is not.
    billing_markers = (
        "no credits remaining", "insufficient_quota", "insufficient quota",
        "credit balance is too low", "billing", "exceeded your current quota",
        "quota exceeded", "resource_exhausted", "spend", "payment",
        "add credits",
    )
    # A dead / invalid / unauthorized key.
    auth_markers = (
        "invalid_api_key", "invalid api key", "incorrect api key",
        "invalid x-api-key", "authenticationerror", "permission_denied",
        "api key not valid", "api_key_invalid", "401", "unauthorized",
    )
    # Temporary rate limiting (key + credits fine, too many requests).
    rate_markers = ("rate limit", "rate_limit", "too many requests",
                    "overloaded", "429")
    # Model id wrong / not accessible.
    notfound_markers = ("model_not_found", "does not exist", "notfounderror",
                        "404", "not found", "unknown model")
    network_markers = ("could not reach", "connectionerror", "timed out",
                       "timeout", "getaddrinfo", "network", "ssl",
                       "failed to establish")

    # Check modality first: its messages often also carry "400"/"invalid".
    if has(*modality_markers):
        return ErrorHelp(
            "modality",
            f"{label}: this model can't accept images",
            "The selected model doesn't support image input, so it can't read "
            "a diagram. Pick a vision / multimodal model (one that accepts "
            "images) and run again — use Fetch models or a recommended model.",
            spec.models_doc_url, "Open model docs")

    if has(*auth_markers) and not has("no credits remaining",
                                      "insufficient_quota"):
        return ErrorHelp(
            "auth",
            f"{label} rejected the API key",
            "The key is missing, invalid, or not authorized for this model. "
            "Re-run Set up / Connect and paste a fresh key.",
            spec.api_keys_url, "Open API keys page")

    if has(*billing_markers):
        return ErrorHelp(
            "billing",
            f"{label}: out of credits / billing not active",
            "Your key is valid, but the account has no usable balance. Add "
            "credits or enable billing for this account, then try again.",
            spec.billing_url or spec.api_keys_url, "Open billing page")

    if has(*notfound_markers):
        return ErrorHelp(
            "not_found",
            f"{label} doesn't recognize that model",
            "The model id may be wrong or not enabled for your account. Use "
            "Fetch models to list ids your key can call.",
            spec.models_doc_url, "Open model docs")

    if has(*rate_markers):
        return ErrorHelp(
            "rate_limit",
            f"{label} rate limit hit",
            "Too many requests for now (the key and credits are fine). Wait a "
            "moment and try again, or slow down the request rate.",
            spec.models_doc_url, "Rate-limit docs")

    if has(*network_markers):
        return ErrorHelp(
            "network",
            f"Couldn't reach {label}",
            "A network/proxy/TLS problem blocked the request. Check your "
            "connection and that the API host is reachable.",
            "", "")

    return ErrorHelp(
        "unknown",
        f"{label} request failed",
        "The call failed for a reason PictoSync couldn't classify. See the "
        "details below.",
        "", "")


class BaseVisionProvider:
    """Interface implemented by every vision provider adapter."""

    spec: ProviderSpec

    def extract(self, model: str, image_path: str, prompt: str,
                api_key: str) -> VisionResponse:
        """Run a single vision call.

        Args:
            model: The model id to invoke.
            image_path: Path to the image to analyze.
            prompt: The fully built extraction prompt.
            api_key: The resolved API key.

        Returns:
            A :class:`VisionResponse` with the raw text and token count.

        Raises:
            ProviderError: If the SDK is missing or the API call fails.
        """
        raise NotImplementedError

    def list_models(self, api_key: str) -> List[ModelInfo]:
        """Return models the key can use (best-effort, vision-capable first).

        Args:
            api_key: The resolved API key.

        Returns:
            A list of :class:`ModelInfo`. May be empty if the vendor has no
            discovery endpoint.

        Raises:
            ProviderError: If the discovery call fails.
        """
        raise NotImplementedError
