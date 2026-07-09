# FixtureForge AI v0.6 – Parser-first, no OCR crash

This version removes Gemini, RapidOCR and OpenCV completely.

Workflow:
PDF with real text → local PDF text extraction → OpenRouter free text model → Universal Fixture JSON → review/export.

For scanned/image-only PDFs:
- The app will not crash.
- It shows page previews.
- Use the manual text/OCR paste fallback, or later add a paid/free vision model.

## Streamlit Secrets

```toml
OPENROUTER_API_KEY = "sk-or-v1-..."
```

Optional:

```toml
OPENROUTER_MODEL = "mistralai/mistral-small-3.2-24b-instruct:free"
```

## Recommended model

```text
mistralai/mistral-small-3.2-24b-instruct:free
```

If unavailable, use any OpenRouter `:free` text/instruct model.
