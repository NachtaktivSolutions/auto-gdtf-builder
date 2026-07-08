# FixtureForge AI v0.3.2

KI-gestützter Fixture-Interpreter für DMX-Manuals.

## Features

- PDF/JPG/PNG Upload
- Gemini Analyse mit Universal Fixture JSON
- bearbeitbare Kanal-Tabelle
- Prompt-Training über bestätigte Korrekturen
- Import/Export von Trainingsdaten als JSONL
- Export als GDTF oder Daslight/Wolfmix CSV

## Streamlit Secrets

In Streamlit unter Settings → Secrets eintragen:

```toml
GEMINI_API_KEY = "dein_gemini_api_key"
```

## Lernen / Training

Das System nutzt am Anfang Prompt-Training:

1. Manual hochladen
2. KI analysiert Fixture
3. Tabelle korrigieren
4. Korrektur übernehmen
5. Korrektur als Trainingsdaten merken
6. Trainingsdaten herunterladen
7. Beim nächsten Mal die JSONL-Datei links importieren

Echtes Fine-Tuning kommt später, wenn genug geprüfte Beispiele vorhanden sind.
