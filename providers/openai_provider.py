"""
providers/openai_provider.py

OpenAI (GPT vision) adapter. Wraps the ``openai`` SDK chat-completions API
with an inline base64 image part.
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
    id="openai",
    label="OpenAI (GPT vision)",
    default_env_key="OPENAI_API_KEY",
    install_hint="pip install openai",
    models_doc_url="https://platform.openai.com/docs/models",
    starter_models=["gpt-4o", "gpt-4.1"],
    pip_package="openai",
    import_module="openai",
    api_keys_url="https://platform.openai.com/api-keys",
    billing_url="https://platform.openai.com/settings/organization/billing/overview",
)


class OpenAIProvider(BaseVisionProvider):
    """Vision provider backed by OpenAI chat completions."""

    spec = SPEC

    def _client(self, api_key: str):
        try:
            from openai import OpenAI
        except Exception as exc:  # pragma: no cover - import guard
            raise ProviderError(
                "openai is not installed. " + self.spec.install_hint
            ) from exc
        return OpenAI(api_key=api_key)

    def extract(self, model: str, image_path: str, prompt: str,
                api_key: str) -> VisionResponse:
        client = self._client(api_key)
        b64, media = image_to_base64(image_path)
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media};base64,{b64}",
                            },
                        },
                    ],
                }],
            )
        except Exception as exc:
            raise ProviderError(f"{type(exc).__name__}: {exc}") from exc

        text = ""
        finish = ""
        try:
            text = response.choices[0].message.content or ""
            finish = getattr(response.choices[0], "finish_reason", "") or ""
        except Exception:
            text = ""
        tokens = 0
        usage = getattr(response, "usage", None)
        if usage is not None:
            tokens = getattr(usage, "total_tokens", 0) or 0
        return VisionResponse(text=text, tokens=tokens, stop_reason=finish,
                              truncated=(finish == "length"))

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
            rows.append(ModelInfo(name=name))
        rows.sort(key=lambda r: r.name)
        return rows
