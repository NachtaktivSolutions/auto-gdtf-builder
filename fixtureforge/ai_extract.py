from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from google import genai
from google.genai import types
from .schema import Fixture
from .prompts import SYSTEM_PROMPT

JSON_SCHEMA: dict[str, Any] = Fixture.model_json_schema()

def extract_fixture_with_gemini(
    api_key: str,
    file_path: str,
    model: str = "gemini-2.0-flash",
    knowledge_context: str = "",
) -> Fixture:
    """Upload a manual/image to Gemini and extract the universal Fixture JSON."""
    client = genai.Client(api_key=api_key)
    path = Path(file_path)
    uploaded = client.files.upload(file=str(path))

    prompt = """
Analysiere diese Datei und extrahiere die komplette Fixture/DMX-Struktur als JSON.

Wende diese FixtureForge-Korrekturregeln und Trainingsbeispiele an, falls vorhanden:
""".strip()
    if knowledge_context.strip():
        prompt += "\n\n" + knowledge_context.strip()
    else:
        prompt += "\n\nKeine zusätzlichen Trainingsregeln vorhanden."

    response = client.models.generate_content(
        model=model,
        contents=[uploaded, prompt],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=JSON_SCHEMA,
            temperature=0.1,
        ),
    )
    text = response.text or "{}"
    data = json.loads(text)
    return Fixture.model_validate(data)
