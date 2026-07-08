# FixtureForge AI v0.3

KI-gestützter DMX Manual -> Fixture Exporter.

## Streamlit Secrets

```toml
GEMINI_API_KEY = "dein_gemini_api_key"
```

## Start lokal

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Workflow

1. PDF/JPG/PNG hochladen
2. KI extrahiert Fixture-Daten + DMX-Kanäle
3. Tabelle prüfen/korrigieren
4. Korrektur als Trainingsdaten speichern
5. Export als GDTF oder Daslight/Wolfmix CSV

Hinweis: Der GDTF-Export ist ein MVP-Exporter und muss mit GDTF Builder/grandMA3 getestet werden.


## v0.3.1
- Passwortsperre entfernt.
- KI-Analyse über Gemini ist bereits eingebaut. Benötigt nur `GEMINI_API_KEY` in Streamlit Secrets.
