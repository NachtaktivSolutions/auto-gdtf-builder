from __future__ import annotations

import json
from typing import Any, Dict
import requests

from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL, APP_URL


SYSTEM_PROMPT = """
You are FixtureForge AI, a professional lighting-fixture DMX interpreter.
You receive extracted text from DMX manuals or DMX charts.
Return ONLY valid JSON. No markdown. No explanation.
Map German/English DMX terms to attributes:
PAN -> Pan, PAN fine/16bit -> PanFine, TILT -> Tilt, TILT fine -> TiltFine,
Dimmerintensität -> Dimmer, Rot -> ColorAdd_R, Grün -> ColorAdd_G, Blau -> ColorAdd_B, Weiß -> ColorAdd_W,
Strobe -> Shutter, Geschwindigkeit PAN/TILT -> PanTiltSpeed, Farbmakros -> ColorMacro,
Bewegungsmakros -> PanTiltMacro, Reset -> Reset, Musikgesteuert -> SoundControl.

JSON structure:
{
  "manufacturer": "string or null",
  "fixture_name": "string or null",
  "notes": "string",
  "physical": {"pan_degrees": null, "tilt_degrees": null, "beam_angle_degrees": null, "weight_kg": null, "width_mm": null, "height_mm": null, "depth_mm": null},
  "modes": [{"name": "string", "channel_count": 0, "confidence": 0.0, "channels": [{"channel": 1, "fine_channel": null, "attribute": "string", "raw_label": "string", "raw_description": "string", "geometry": null, "default_value": null, "highlight_value": null, "ranges": [{"from": 0, "to": 255, "name": "string", "description": "string"}]}]}],
  "warnings": ["string"]
}
"""


def analyze_text_with_openrouter(manual_text: str, model: str | None = None, extra_context: str = "", timeout_seconds: int = 120) -> Dict[str, Any]:
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is missing in Streamlit Secrets.")

    selected_model = model or OPENROUTER_MODEL
    payload = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\\n{extra_context}\\n\\nManual/OCR text:\\n{manual_text}"}
        ],
        "temperature": 0.05,
        "response_format": {"type": "json_object"}
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": APP_URL,
        "X-Title": "FixtureForge AI"
    }
    r = requests.post(OPENROUTER_BASE_URL, headers=headers, json=payload, timeout=timeout_seconds)
    if r.status_code >= 400:
        raise RuntimeError(f"OpenRouter error {r.status_code}: {r.text[:2500]}")
    data = r.json()
    text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    try:
        return json.loads(text)
    except Exception:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end+1])
        raise RuntimeError("OpenRouter did not return JSON: " + text[:1000])
