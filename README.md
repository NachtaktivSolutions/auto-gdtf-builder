# FixtureForge AI v0.3.3

KI-gestützter Fixture-Interpreter für DMX-Manuals.

## Neu in v0.3.3

- Kein Passwortschutz
- robusterer Gemini-Aufruf ohne problematisches striktes Response-Schema
- bessere Fehlermeldungen in der App
- Modellauswahl mit `gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-1.5-flash`
- Referenz-Training: funktionierende `.gdtf` hochladen und als Lernkontext nutzen

## Streamlit Secrets

```toml
GEMINI_API_KEY = "dein_gemini_api_key"
```

## Ablauf

1. Optional: funktionierende GDTF in der Sidebar als Referenztraining hochladen.
2. Manual/PDF/JPG/PNG hochladen.
3. KI-Analyse starten.
4. Kanäle/Values korrigieren.
5. Korrektur als Trainingsdaten merken.
6. Trainingsdaten als JSONL herunterladen und später wieder importieren.
7. GDTF oder Daslight/Wolfmix CSV exportieren.
