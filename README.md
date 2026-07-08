# Auto GDTF Generator - Streamlit Starter

KI-gestützter MVP für: Manual / DMX-Sheet hochladen → Kanalmap extrahieren → prüfen → `.gdtf` erzeugen.

## Kostenloser Stack

- Streamlit Community Cloud
- GitHub Repo
- Gemini API Free Tier

## Dateien

- `streamlit_app.py` – Haupt-App
- `ai_extract.py` – Gemini-Analyse
- `gdtf_builder.py` – GDTF/CSV-Erzeugung
- `schema.py` – interne Struktur / Attribute
- `prompts.py` – Prompt für die KI
- `requirements.txt` – Python-Abhängigkeiten
- `.streamlit/config.toml` – Streamlit Theme
- `.streamlit/secrets.toml.example` – Beispiel für Secrets

## Deployment in Streamlit

Bei Streamlit Deploy:

- Repository: `DEINUSER/auto-gdtf-generator`
- Branch: `main` oder `master`, je nach GitHub Repo
- Main file path: `streamlit_app.py`
- App URL optional: z. B. `auto-gdtf-generator`

## Secrets

In Streamlit Cloud unter App → Settings → Secrets eintragen:

```toml
GEMINI_API_KEY = "dein_gemini_api_key"
APP_PASSWORD = "ein-passwort"
```

Der Key darf niemals direkt im Code stehen.

## Wichtige Hinweise

- Die KI erzeugt kein GDTF direkt, sondern eine Zwischenstruktur (`fixture.json`).
- Der Generator baut daraus deterministisch eine `.gdtf` Datei.
- Die GDTF muss in grandMA3 / GDTF Builder getestet werden.
- Für perfekte Ergebnisse braucht es Feedback und Geräte-Tests.

## Nächste Ausbaustufen

- Bessere GDTF-Validierung
- GDTF Builder Schema Check
- Login / Projekte speichern
- Trainingsbeispiele: Manual + geprüfte fixture.json + funktionierende GDTF
- Multi-Instance-Assistent für Bars, Tubes und Pixel-Fixtures
