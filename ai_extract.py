import json
import os
import re
import tempfile
from typing import Any, Dict

import google.generativeai as genai

from prompts import SYSTEM_PROMPT, USER_PROMPT


def _strip_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end >= start:
        text = text[start:end+1]
    return text


def extract_fixture_json(uploaded_file, api_key: str, model_name: str = "gemini-1.5-flash") -> Dict[str, Any]:
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY fehlt. Bitte in Streamlit Secrets eintragen.")
    genai.configure(api_key=api_key)
    suffix = os.path.splitext(uploaded_file.name)[1] or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    try:
        uploaded = genai.upload_file(tmp_path, display_name=uploaded_file.name)
        model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)
        response = model.generate_content([USER_PROMPT, uploaded], generation_config={"temperature": 0.1})
        raw = response.text or ""
        data = json.loads(_strip_json(raw))
        return data
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
