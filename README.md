# FixtureForge AI v0.5 – OCR + OpenRouter Text Model

This version removes Gemini and removes Vision-model dependency.

Workflow:
PDF/JPG/PNG → local OCR → extracted DMX text → OpenRouter text model → Universal Fixture JSON → review/export.

## Streamlit Secrets

```toml
OPENROUTER_API_KEY = "sk-or-v1-..."
```

Optional:

```toml
OPENROUTER_MODEL = "mistralai/mistral-small-3.2-24b-instruct:free"
```

## Recommended free OpenRouter model

Use:

```text
mistralai/mistral-small-3.2-24b-instruct:free
```

If this is unavailable, use any current OpenRouter text model with `:free`, preferably Mistral/Qwen/Llama Instruct.
