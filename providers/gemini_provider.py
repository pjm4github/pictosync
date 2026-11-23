"""
providers/gemini_provider.py

Google Gemini vision adapter. Wraps the ``google-genai`` SDK and the Gemini
REST models endpoint used for discovery.
"""

from __future__ import annotations

from typing import List

from providers.base import (
    BaseVisionProvider,
    ModelInfo,
    ProviderError,
    ProviderSpec,
    VisionResponse,
)

SPEC = ProviderSpec(
    id="gemini",
    label="Google Gemini",
    default_env_key="GOOGLE_API_KEY",
    install_hint="pip install google-genai",
    models_doc_url="https://ai.google.dev/gemini-api/docs/models",
    starter_models=["gemini-2.5-flash-image", "gemini-3-pro-image-preview"],
    pip_package="google-genai",
    import_module="google.genai",
    api_keys_url="https://aistudio.google.com/apikey",
    billing_url="https://aistudio.google.com/app/plan_information",
)


class GeminiProvider(BaseVisionProvider):
    """Vision provider backed by Google Gemini."""

    spec = SPEC

    def extract(self, model: str, image_path: str, prompt: str,
                api_key: str) -> VisionResponse:
        try:
            from google import genai
        except Exception as exc:  # pragma: no cover - import guard
            raise ProviderError(
                "google-genai is not installed. " + self.spec.install_hint
            ) from exc
        try:
            from PIL import Image
        except Exception as exc:  # pragma: no cover - import guard
            raise ProviderError("Pillow is not installed. pip install pillow") from exc

        try:
            client = genai.Client(api_key=api_key)
            img = Image.open(image_path)
            response = client.models.generate_content(
                model=model,
                contents=[prompt, img],
            )
        except Exception as exc:
            raise ProviderError(f"{type(exc).__name__}: {exc}") from exc

        text = getattr(response, "text", None) or ""
        tokens = 0
        usage = getattr(response, "usage_metadata", None)
        if usage:
            tokens = getattr(usage, "total_token_count", 0) or 0
        stop = ""
        try:
            cand = (getattr(response, "candidates", None) or [None])[0]
            fr = getattr(cand, "finish_reason", "")
            stop = getattr(fr, "name", "") or str(fr or "")
        except Exception:
            stop = ""
        return VisionResponse(text=text, tokens=tokens, stop_reason=stop,
                              truncated=(stop.upper() == "MAX_TOKENS"))

    def list_models(self, api_key: str) -> List[ModelInfo]:
        import json
        import ssl
        import urllib.error
        import urllib.request

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models"
            f"?key={api_key}&pageSize=1000"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "PictoSync"})
        try:
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", "ignore")[:400]
            except Exception:
                pass
            raise ProviderError(
                f"HTTP {exc.code} from Gemini models endpoint. "
                f"{body or exc}"
            ) from exc
        except Exception as exc:
            raise ProviderError(f"{type(exc).__name__}: {exc}") from exc

        rows: List[ModelInfo] = []
        for m in data.get("models", []) or []:
            methods = (
                m.get("supportedGenerationMethods")
                or m.get("supported_generation_methods")
                or []
            )
            if "generateContent" not in methods:
                continue
            name = (m.get("name", "") or "").split("/")[-1]
            if not name:
                continue
            tin = m.get("inputTokenLimit") or m.get("input_token_limit") or ""
            rows.append(ModelInfo(
                name=name,
                display=m.get("displayName") or m.get("display_name") or name,
                detail=f"in {tin}" if tin else "",
            ))
        rows.sort(key=lambda r: r.name)
        return rows
