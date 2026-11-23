"""
providers/anthropic_provider.py

Anthropic (Claude vision) adapter. Wraps the ``anthropic`` SDK Messages API
with an inline base64 image block.
"""

from __future__ import annotations

from typing import List

from providers.base import (
    BaseVisionProvider,
    ModelInfo,
    ProviderError,
    ProviderSpec,
    VisionResponse,
    image_to_base64,
)

SPEC = ProviderSpec(
    id="anthropic",
    label="Anthropic (Claude vision)",
    default_env_key="ANTHROPIC_API_KEY",
    install_hint="pip install anthropic",
    models_doc_url="https://docs.anthropic.com/en/docs/about-claude/models",
    starter_models=["claude-opus-4-8", "claude-sonnet-5-5"],
    pip_package="anthropic",
    import_module="anthropic",
    api_keys_url="https://console.anthropic.com/settings/keys",
    billing_url="https://console.anthropic.com/settings/billing",
)

# Claude needs an explicit output budget. Extraction JSON can be large, so
# keep this high to avoid truncating a big diagram's annotations mid-object.
_MAX_TOKENS = 16384


class AnthropicProvider(BaseVisionProvider):
    """Vision provider backed by Anthropic Claude."""

    spec = SPEC

    def _client(self, api_key: str):
        try:
            from anthropic import Anthropic
        except Exception as exc:  # pragma: no cover - import guard
            raise ProviderError(
                "anthropic is not installed. " + self.spec.install_hint
            ) from exc
        return Anthropic(api_key=api_key)

    def extract(self, model: str, image_path: str, prompt: str,
                api_key: str) -> VisionResponse:
        client = self._client(api_key)
        b64, media = image_to_base64(image_path)
        try:
            response = client.messages.create(
                model=model,
                max_tokens=_MAX_TOKENS,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media,
                                "data": b64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }],
            )
        except Exception as exc:
            raise ProviderError(f"{type(exc).__name__}: {exc}") from exc

        text = ""
        for block in getattr(response, "content", []) or []:
            if getattr(block, "type", "") == "text":
                text += getattr(block, "text", "") or ""
        tokens = 0
        usage = getattr(response, "usage", None)
        if usage is not None:
            tokens = (getattr(usage, "input_tokens", 0) or 0) + (
                getattr(usage, "output_tokens", 0) or 0)
        stop = getattr(response, "stop_reason", "") or ""
        return VisionResponse(text=text, tokens=tokens, stop_reason=stop,
                              truncated=(stop == "max_tokens"))

    def list_models(self, api_key: str) -> List[ModelInfo]:
        client = self._client(api_key)
        try:
            resp = client.models.list()
        except Exception as exc:
            raise ProviderError(f"{type(exc).__name__}: {exc}") from exc
        rows: List[ModelInfo] = []
        for m in getattr(resp, "data", []) or []:
            name = getattr(m, "id", "") or ""
            if not name:
                continue
            rows.append(ModelInfo(
                name=name,
                display=getattr(m, "display_name", "") or name,
            ))
        rows.sort(key=lambda r: r.name)
        return rows
