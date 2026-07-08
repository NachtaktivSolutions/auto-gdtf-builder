from __future__ import annotations
import json, re, time
from pathlib import Path
from google import genai
from google.genai import types
from .schema import Fixture
from .prompts import SYSTEM_PROMPT


def _extract_json(text: str) -> dict:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    # find first JSON object if model added text
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end+1]
    return json.loads(text)


def extract_fixture_with_gemini(
    api_key: str,
    file_path: str,
    model: str = "gemini-2.5-flash",
    knowledge_context: str = "",
) -> Fixture:
    """Upload a manual/image to Gemini and extract the universal Fixture JSON.

    This version intentionally does not use strict response_schema because some
    Gemini endpoints reject complex Pydantic schemas with nested $defs/anyOf.
    Instead, the schema is included in the prompt and validated locally.
    """
    if not api_key or not api_key.strip():
        raise RuntimeError("GEMINI_API_KEY fehlt. Bitte in Streamlit → Settings → Secrets eintragen.")

    client = genai.Client(api_key=api_key.strip())
    path = Path(file_path)
    uploaded = client.files.upload(file=str(path))

    # Some file types can briefly stay in PROCESSING. Poll a little.
    try:
        for _ in range(20):
            state = getattr(getattr(uploaded, "state", None), "name", None) or str(getattr(uploaded, "state", ""))
            if "PROCESS" not in state.upper():
                break
            time.sleep(1)
            uploaded = client.files.get(name=uploaded.name)
    except Exception:
        pass

    schema_hint = Fixture.model_json_schema()
    prompt = f"""
Analysiere die hochgeladene Datei und extrahiere die komplette Fixture/DMX-Struktur.

Gib AUSSCHLIESSLICH gültiges JSON zurück. Kein Markdown, keine Erklärung.
Das JSON muss logisch diesem Schema entsprechen:
{json.dumps(schema_hint, ensure_ascii=False)[:16000]}

Wende diese FixtureForge-Korrekturregeln und Trainingsbeispiele an, falls vorhanden:
{knowledge_context.strip() if knowledge_context.strip() else 'Keine zusätzlichen Trainingsregeln vorhanden.'}

Wichtige Regeln:
- channel_count muss zur DMX-Mode-Kanalzahl passen.
- Mehrere DMX-Modi separat in modes[] ablegen.
- Values als from_value/to_value/label speichern.
- Fine-Kanäle resolution="fine" und fine_of=<coarse channel>.
- Grobe Pan/Tilt bei 16 Bit resolution="coarse".
- Normale Kanäle resolution="8bit".
""".strip()

    try:
        response = client.models.generate_content(
            model=model,
            contents=[uploaded, prompt],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
    except Exception as e:
        msg = str(e)
        raise RuntimeError(
            "Gemini konnte die Datei nicht analysieren. Prüfe bitte: API-Key in Secrets, Free-Tier-Limit, Modellname, Dateigröße/Dateityp. "
            f"Originalfehler: {msg[:800]}"
        ) from e

    text = response.text or "{}"
    try:
        data = _extract_json(text)
        return Fixture.model_validate(data)
    except Exception as e:
        raise RuntimeError(
            "Gemini hat keine gültige Fixture-JSON-Struktur geliefert. "
            f"Antwort-Anfang: {text[:1000]}"
        ) from e
