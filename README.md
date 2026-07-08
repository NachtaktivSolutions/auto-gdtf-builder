# FixtureForge AI v0.3.4

Fix-Version für image-only PDFs:
- PDFs werden lokal mit PyMuPDF in PNG-Seiten gerendert
- Gemini bekommt die Seiten als Bilder statt als langsamen File-Upload
- Standardmodell auf `gemini-2.0-flash` gesetzt
- bessere Fehlerausgabe

Streamlit Secrets:
```toml
GEMINI_API_KEY = "dein_key"
```
