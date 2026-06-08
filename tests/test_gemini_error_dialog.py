"""
tests/test_gemini_error_dialog.py

The Auto-Extract failure dialog classifies raw Gemini/worker errors into a
friendly (title, summary, how-to-fix) triple, keeping the raw text for the
collapsible Details section.
"""
from __future__ import annotations

import pytest

from main import MainWindow


CASES = {
    "Gemini quota exceeded":
        "429 RESOURCE_EXHAUSTED. {'error': {'code': 429, 'message': "
        "'You exceeded your current quota'}}\nTraceback (most recent call last):",
    "Gemini authentication failed":
        "403 PERMISSION_DENIED: API key not valid",
    "Gemini model not available":
        "404 NOT_FOUND: models/gemini-x is not found for API version v1",
    "Gemini API key not set":
        "RuntimeError: GOOGLE_API_KEY is not set.",
    "Gemini SDK not installed":
        "RuntimeError: google-genai not installed. pip install google-genai",
    "Could not reach Gemini":
        "ConnectionError: failed to establish a new connection: getaddrinfo failed",
    "Auto-Extract failed":
        "ValueError: something unexpected",
}


@pytest.mark.parametrize("expected_title,raw", list(CASES.items()))
def test_classification(qapp, expected_title, raw):
    title, summary, how_to_fix = MainWindow._friendly_gemini_error(raw)
    assert title == expected_title
    assert summary.strip()
    assert how_to_fix.strip()


def test_quota_message_mentions_remedies(qapp):
    raw = "429 RESOURCE_EXHAUSTED quota exceeded, model gemini-3-pro-image, limit: 0"
    title, summary, how_to_fix = MainWindow._friendly_gemini_error(raw)
    assert title == "Gemini quota exceeded"
    # Actionable: points at the model setting and billing/rate-limit docs.
    assert "Default Model" in how_to_fix
    assert "rate-limits" in how_to_fix
