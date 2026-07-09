# FixtureForge AI v0.7 – Working Streamlit Build

This build is designed to actually start on Streamlit Cloud.

Removed:
- Gemini
- RapidOCR
- OpenCV
- libGL dependency

Added:
- System Tesseract via `packages.txt`
- `pytesseract`
- Local PDF rendering with PyMuPDF
- Local OCR fallback
- Built-in Eurolite LED TMH Bar B240 parser/template
- Optional OpenRouter text-model analysis

## Streamlit Secrets

OpenRouter is optional in this version.

```toml
OPENROUTER_API_KEY = "sk-or-v1-..."
OPENROUTER_MODEL = "mistralai/mistral-small-3.2-24b-instruct:free"
```

If OpenRouter has no free credits/model, the built-in B240 parser still works for the B240 manual.

## Main file path

```text
streamlit_app.py
```
