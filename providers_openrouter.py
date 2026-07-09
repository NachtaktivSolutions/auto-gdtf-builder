from __future__ import annotations

import base64
import json
from typing import Any, Dict, List, Tuple

import requests

from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, DEFAULT_OPENROUTER_MODEL, APP_URL
from prompts import SYSTEM_PROMPT, USER_PROMPT


class OpenRouterError(RuntimeError):
    pass


def _image_to_data_url(image_bytes: bytes, mime: str = "image/png") -> str:
    b64 = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime};base64,{b64}"


def analyze_images_with_openrouter(
    images: List[Tuple[str, bytes]],
    model: str | None = None,
    extra_context: str = "",
    timeout_seconds: int = 120,
) -> Dict[str, Any]:
    if not OPENROUTER_API_KEY:
        raise OpenRouterError("OPENROUTER_API_KEY is missing in Streamlit Secrets.")

    if not images:
        raise OpenRouterError("No images provided for analysis.")

    selected_model = model or DEFAULT_OPENROUTER_MODEL

    content = [{"type": "text", "text": USER_PROMPT + "\n\n" + extra_context.strip()}]
    for name, img_bytes in images:
        content.append({"type": "text", "text": f"Image: {name}"})
        content.append({
            "type": "image_url",
            "image_url": {"url": _image_to_data_url(img_bytes)}
        })

    payload = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        "temperature": 0.1,
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
        raise OpenRouterError(f"OpenRouter error {response.status_code}: {response.text[:2000]}")

    data = response.json()
    try:
        text = data["choices"][0]["message"]["content"]
    except Exception as exc:
        raise OpenRouterError(f"Unexpected OpenRouter response: {json.dumps(data)[:2000]}") from exc

    if isinstance(text, list):
        text = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end+1])
        raise OpenRouterError(f"Model did not return valid JSON. Raw response: {text[:2000]}")
