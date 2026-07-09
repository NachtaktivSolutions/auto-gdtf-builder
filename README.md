# FixtureForge AI v0.4 – OpenRouter Only

Streamlit MVP for uploading DMX manuals / DMX sheet images and extracting a Universal Fixture JSON using OpenRouter.

## Streamlit Secrets

In Streamlit Cloud → App → Settings → Secrets:

```toml
OPENROUTER_API_KEY = "your_openrouter_key"
```

Optional:

```toml
OPENROUTER_MODEL = "qwen/qwen2.5-vl-72b-instruct"
```

## Deploy

Main file path:

```text
streamlit_app.py
```

## Current features

- PDF/JPG/PNG upload
- PDF pages are converted to PNG images locally
- OpenRouter-only analysis
- Gemini removed completely
- Universal Fixture JSON output
- editable channel table
- export:
  - JSON
  - CSV for Daslight/Wolfmix manual fixture creation
  - basic GDTF package placeholder export

v0.4 focuses on reliable AI extraction and project structure.
