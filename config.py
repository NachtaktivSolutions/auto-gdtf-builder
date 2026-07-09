import streamlit as st

APP_NAME = "FixtureForge AI"
APP_VERSION = "0.4.0"

DEFAULT_OPENROUTER_MODEL = st.secrets.get(
    "OPENROUTER_MODEL",
    "qwen/qwen2.5-vl-72b-instruct"
)

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

APP_URL = "https://fixtureforge.local"
