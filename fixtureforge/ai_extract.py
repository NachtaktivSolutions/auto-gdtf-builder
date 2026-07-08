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
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end+1]
    return json.loads(text)


def _render_pdf_to_png_bytes(path: Path, max_pages: int = 9, zoom: float = 1.6) -> list[bytes]:
    """Render image-only PDFs to PNG pages. This avoids slow Gemini file processing."""
    import fitz  # PyMuPDF
    pages: list[bytes] = []
    doc = fitz.open(str(path))
    for i in range(min(len(doc), max_pages)):
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        pages.append(pix.tobytes("png"))
    doc.close()
    return pages


def _build_prompt(knowledge_context: str) -> str:
    schema_hint = Fixture.model_json_schema()
    return f"""
Analysiere die hochgeladene Datei/Bilder und extrahiere die komplette Fixture/DMX-Struktur.

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
- Bei Tabellen mit mehreren Modus-Spalten die Kanalnummern pro Mode korrekt übernehmen.
- Wenn ein Wertbereich wie 0-10 keine Funktion und 11-255 Strobe ist, beide ranges anlegen.
""".strip()


def extract_fixture_with_gemini(
    api_key: str,
    file_path: str,
    model: str = "gemini-2.0-flash",
    knowledge_context: str = "",
) -> Fixture:
    """Extract universal Fixture JSON.

    v0.3.4: PDFs werden lokal in PNG-Seiten gerendert und als Bilder an Gemini gesendet.
    Das ist bei DMX-Sheets deutlich zuverlässiger als Gemini File Upload für image-only PDFs.
    """
    if not api_key or not api_key.strip():
        raise RuntimeError("GEMINI_API_KEY fehlt. Bitte in Streamlit → Settings → Secrets eintragen.")

    client = genai.Client(api_key=api_key.strip())
    path = Path(file_path)
    prompt = _build_prompt(knowledge_context)

    contents = [prompt]
    used_inline_images = False

    if path.suffix.lower() == ".pdf":
        try:
            pages = _render_pdf_to_png_bytes(path, max_pages=9, zoom=1.6)
            if pages:
                used_inline_images = True
                contents.append("\nDie folgenden Bilder sind gerenderte Seiten des PDF-Manuals/DMX-Sheets in Reihenfolge. Lies insbesondere die Tabellen und Modus-Spalten.")
                for idx, data in enumerate(pages, start=1):
                    contents.append(f"\n--- PDF Seite {idx} ---")
                    contents.append(types.Part.from_bytes(data=data, mime_type="image/png"))
        except Exception:
            # Fallback below via file upload
            used_inline_images = False

    if not used_inline_images:
        if path.suffix.lower() in [".png", ".jpg", ".jpeg"]:
            mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
            contents.append(types.Part.from_bytes(data=path.read_bytes(), mime_type=mime))
        else:
            uploaded = client.files.upload(file=str(path))
            try:
                for _ in range(15):
                    state = getattr(getattr(uploaded, "state", None), "name", None) or str(getattr(uploaded, "state", ""))
                    if "PROCESS" not in state.upper():
                        break
                    time.sleep(1)
                    uploaded = client.files.get(name=uploaded.name)
            except Exception:
                pass
            contents.append(uploaded)

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
    except Exception as e:
        msg = str(e)
        raise RuntimeError(
            "Gemini konnte die Datei nicht analysieren. Prüfe: API-Key, Free-Tier-Limit, Modellname und ob das Projekt in Google AI Studio für die Gemini API freigeschaltet ist. "
            f"Originalfehler: {msg[:1200]}"
        ) from e

    text = response.text or "{}"
    try:
        data = _extract_json(text)
        return Fixture.model_validate(data)
    except Exception as e:
        raise RuntimeError(
            "Gemini hat keine gültige Fixture-JSON-Struktur geliefert. "
            f"Antwort-Anfang: {text[:1200]}"
        ) from e
