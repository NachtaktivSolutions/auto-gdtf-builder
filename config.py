import streamlit as st

APP_NAME = "Nachtaktiv GDTF Builder"
APP_VERSION = "0.15.0"

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL", "mistralai/mistral-small-3.2-24b-instruct:free")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
APP_URL = "https://nachtaktiv-gdtf-builder.streamlit.app"
