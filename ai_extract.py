import base64
import json
import os
import re
from typing import Any, Dict, Optional

import requests
import streamlit as st

from prompts import SYSTEM_PROMPT, USER_TEMPLATE


def _get_secret(name: str) -> Optional[str]:
    try:
        value = st.secrets.get(name)
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name)


def _extract_json(text: str) -> Dict[str, Any]:
    """Robuste JSON-Extraktion aus Modellantworten."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text, flags=re.I).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            raise
        return json.loads(match.group(0))


def _read_interactions_text(payload: Dict[str, Any]) -> str:
    """Extrahiert Text aus unterschiedlichen Gemini REST-Antwortformen."""
    if "output_text" in payload:
        return payload["output_text"]
    steps = payload.get("steps") or []
    if steps:
        content = steps[-1].get("content") or []
        texts = []
        for part in content:
            if isinstance(part, dict) and part.get("text"):
                texts.append(part["text"])
        if texts:
            return "\n".join(texts)
    # Fallback fuer generateContent-aehnliche Responses
    candidates = payload.get("candidates") or []
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        texts = [p.get("text", "") for p in parts if isinstance(p, dict)]
        if texts:
            return "\n".join(texts)
    raise RuntimeError(f"Konnte keinen Text in Gemini-Antwort finden: {payload}")


def extract_fixture_with_gemini(
    file_bytes: bytes,
    mime_type: str,
    filename: str,
    manufacturer_hint: str = "",
    model_hint: str = "",
    mode_hint: str = "alle Modi",
    model: str = "gemini-3.5-flash",
) -> Dict[str, Any]:
    """Sendet PDF/Bild inline an Gemini Interactions API und erwartet JSON zurueck.

    Benoetigt Streamlit Secret GEMINI_API_KEY.
    """
    api_key = _get_secret("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY fehlt. Bitte in Streamlit unter App settings -> Secrets eintragen.")

    b64 = base64.b64encode(file_bytes).decode("utf-8")
    if mime_type == "application/pdf":
        file_part = {"type": "document", "data": b64, "mime_type": mime_type}
    elif mime_type.startswith("image/"):
        file_part = {"type": "image", "data": b64, "mime_type": mime_type}
    else:
        # Text/sonstige Dateien als Dokument versuchen
        file_part = {"type": "document", "data": b64, "mime_type": mime_type or "application/octet-stream"}

    user_prompt = USER_TEMPLATE.format(
        manufacturer_hint=manufacturer_hint or "unbekannt",
        model_hint=model_hint or "unbekannt",
        mode_hint=mode_hint or "alle Modi",
    )

    payload = {
        "model": model,
        "input": [
            {"type": "text", "text": SYSTEM_PROMPT},
            file_part,
            {"type": "text", "text": user_prompt},
        ],
    }

    url = "https://generativelanguage.googleapis.com/v1beta/interactions"
    resp = requests.post(
        url,
        headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        json=payload,
        timeout=180,
    )
    if resp.status_code >= 400:
        raise RuntimeError(f"Gemini API Fehler {resp.status_code}: {resp.text[:1200]}")

    text = _read_interactions_text(resp.json())
    data = _extract_json(text)
    data.setdefault("notes", [])
    data["notes"].append(f"Analysiert aus {filename} mit {model}.")
    return data
