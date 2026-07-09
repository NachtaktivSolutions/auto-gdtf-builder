from __future__ import annotations

import json
from typing import Any, Dict

import requests

from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, DEFAULT_OPENROUTER_MODEL, APP_URL
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


class OpenRouterError(RuntimeError):
    pass


def analyze_text_with_openrouter(
    manual_text: str,
    model: str | None = None,
    extra_context: str = "",
    timeout_seconds: int = 120,
) -> Dict[str, Any]:
    if not OPENROUTER_API_KEY:
        raise OpenRouterError("OPENROUTER_API_KEY is missing in Streamlit Secrets.")

    if not manual_text.strip():
        raise OpenRouterError("No text available. Use a text-based PDF or paste OCR/manual text into the fallback field.")

    selected_model = model or DEFAULT_OPENROUTER_MODEL
    prompt = USER_PROMPT_TEMPLATE.format(extra_context=extra_context.strip(), manual_text=manual_text)

    payload = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.05,
        "response_format": {"type": "json_object"},
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": APP_URL,
        "X-Title": "FixtureForge AI",
    }

    response = requests.post(
        OPENROUTER_BASE_URL,
        headers=headers,
        json=payload,
        timeout=timeout_seconds,
    )

    if response.status_code >= 400:
        raise OpenRouterError(f"OpenRouter error {response.status_code}: {response.text[:2500]}")

    data = response.json()
    text = data.get("choices", [{}])[0].get("message", {}).get("content", "")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end+1])
        raise OpenRouterError(f"Model did not return valid JSON. Raw response: {text[:2000]}")
