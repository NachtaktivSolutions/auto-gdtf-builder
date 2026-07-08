# Auto GDTF Builder MVP

Streamlit-App: PDF/Bild eines DMX-Manuals hochladen, KI extrahiert Kanäle/Values, Tabelle korrigieren, Export als GDTF oder Daslight/Wolfmix-Kanalmap.

## Streamlit Secrets

```toml
GEMINI_API_KEY = "dein_key"
APP_PASSWORD = "dein_passwort"
```

## Dateien

- `streamlit_app.py` – Benutzeroberfläche
- `ai_extract.py` – Gemini-Extraktion
- `gdtf_builder.py` – GDTF/CSV Generator
- `daslight_builder.py` – aktuell CSV-Map für Daslight/Wolfmix
- `learning.py` – exportiert Korrekturen als Lernbeispiele
- `schema.py`, `prompts.py` – JSON-Schema und Prompt

## Wichtig

Das ist ein MVP. GDTF-Dateien bitte in GDTF Builder und grandMA3 testen.
