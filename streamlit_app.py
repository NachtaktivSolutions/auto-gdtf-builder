from __future__ import annotations

import traceback
import pandas as pd
import streamlit as st

from config import APP_NAME, APP_VERSION, OPENROUTER_API_KEY, OPENROUTER_MODEL
from pdf_tools import extract_pdf_text, pdf_to_page_images, image_to_png_bytes
from ocr_tools import ocr_images
from b240_template import build_b240_fixture, looks_like_b240
from providers_openrouter import analyze_text_with_openrouter
from models_fixture import normalize_fixture, fixture_to_json_bytes
from exporters import mode_to_dataframe, fixture_to_csv_bytes, build_simple_gdtf


st.set_page_config(page_title=APP_NAME, page_icon="💡", layout="wide")
st.title(f"💡 {APP_NAME}")
st.caption(f"v{APP_VERSION} · working build · no Gemini · no OpenCV · B240 template included")

with st.sidebar:
    st.header("Settings")
    st.write("Provider: OpenRouter optional")
    model = st.text_input("OpenRouter model", value=OPENROUTER_MODEL)
    max_pages = st.slider("Max PDF pages", 1, 30, 9)
    ocr_lang = st.text_input("OCR language", value="deu+eng")
    st.success("OPENROUTER_API_KEY found") if OPENROUTER_API_KEY else st.warning("OpenRouter key missing. Built-in B240 template still works.")
    st.caption("Free text model example: mistralai/mistral-small-3.2-24b-instruct:free")

uploaded = st.file_uploader("PDF, JPG, JPEG or PNG", type=["pdf", "jpg", "jpeg", "png"])
extra_context = st.text_area("Optional context / rules", height=80)
manual_text_fallback = st.text_area("Fallback: paste manual/OCR text here", height=140)

use_b240_template = st.checkbox("Force built-in Eurolite LED TMH Bar B240 template", value=False)
use_ocr = st.checkbox("Run local Tesseract OCR if no embedded text is found", value=True)
use_ai = st.checkbox("Use OpenRouter AI for generic fixture analysis", value=True)

if "fixture" not in st.session_state:
    st.session_state.fixture = None
if "manual_text" not in st.session_state:
    st.session_state.manual_text = ""
if "images" not in st.session_state:
    st.session_state.images = []

def load_file(uploaded_file):
    if uploaded_file is None:
        return "", []
    raw = uploaded_file.getvalue()
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        text = extract_pdf_text(raw, max_pages=max_pages)
        images = pdf_to_page_images(raw, max_pages=max_pages)
        return text, images
    return "", [(uploaded_file.name, image_to_png_bytes(raw))]

if uploaded:
    st.write(f"Uploaded: `{uploaded.name}` · {uploaded.size/1024:.1f} KB")

if st.button("Analyze", type="primary"):
    try:
        text = ""
        images = []
        if uploaded:
            with st.spinner("Reading file..."):
                text, images = load_file(uploaded)
                st.session_state.images = images

        if manual_text_fallback.strip():
            text = manual_text_fallback.strip()

        if use_b240_template or looks_like_b240(uploaded.name if uploaded else "", text):
            st.session_state.fixture = build_b240_fixture()
            st.success("Built-in Eurolite LED TMH Bar B240 template loaded.")
        else:
            if not text.strip() and use_ocr and images:
                with st.spinner("No embedded text found. Running local Tesseract OCR..."):
                    text = ocr_images(images, lang=ocr_lang)
            st.session_state.manual_text = text

            if not text.strip():
                st.warning("No text found. Try OCR, paste text into fallback, or use a model/API with image support.")
            elif use_ai:
                with st.spinner("Analyzing text with OpenRouter..."):
                    raw = analyze_text_with_openrouter(text, model=model, extra_context=extra_context)
                    st.session_state.fixture = normalize_fixture(raw)
                st.success("AI analysis complete.")
            else:
                st.info("Text extracted. Enable OpenRouter AI or use a built-in fixture template.")
    except Exception as exc:
        st.error(str(exc))
        with st.expander("Debug traceback"):
            st.code(traceback.format_exc())

if st.session_state.images:
    with st.expander("Preview pages/images"):
        cols = st.columns(3)
        for idx, (name, img) in enumerate(st.session_state.images[:9]):
            with cols[idx % 3]:
                st.image(img, caption=name, use_container_width=True)

if st.session_state.manual_text:
    with st.expander("Extracted/OCR text"):
        st.text_area("Text", st.session_state.manual_text, height=300)

fixture = st.session_state.fixture
if fixture:
    st.subheader("Fixture")
    c1, c2, c3 = st.columns(3)
    with c1:
        fixture["manufacturer"] = st.text_input("Manufacturer", fixture.get("manufacturer") or "")
    with c2:
        fixture["fixture_name"] = st.text_input("Fixture name", fixture.get("fixture_name") or "")
    with c3:
        st.metric("Modes", len(fixture.get("modes", [])))

    st.subheader("Review Channels")
    for i, mode in enumerate(fixture.get("modes", [])):
        with st.expander(f"{mode.get('name')} · {mode.get('channel_count')} CH", expanded=(mode.get("name") == "48CH")):
            df = mode_to_dataframe(mode)
            edited = st.data_editor(df, use_container_width=True, num_rows="dynamic", key=f"editor_{i}")
            # Simple writeback without parsing ranges from table text
            new_channels = []
            for _, row in edited.iterrows():
                try:
                    ch = int(row.get("channel"))
                except Exception:
                    continue
                fine = row.get("fine_channel")
                try:
                    fine = None if pd.isna(fine) or fine == "" else int(float(fine))
                except Exception:
                    fine = None
                old = next((x for x in mode.get("channels", []) if x.get("channel") == ch), {})
                new_channels.append({
                    "channel": ch,
                    "fine_channel": fine,
                    "attribute": str(row.get("attribute") or ""),
                    "raw_label": str(row.get("raw_label") or ""),
                    "raw_description": str(row.get("raw_description") or ""),
                    "geometry": None if pd.isna(row.get("geometry")) else str(row.get("geometry") or ""),
                    "default_value": old.get("default_value"),
                    "highlight_value": old.get("highlight_value"),
                    "ranges": old.get("ranges", []),
                })
            mode["channels"] = new_channels

    st.subheader("Export")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.download_button("Download JSON", fixture_to_json_bytes(fixture), "fixtureforge_fixture.json", "application/json")
    with col_b:
        st.download_button("Download Daslight/Wolfmix CSV", fixture_to_csv_bytes(fixture), "fixtureforge_channel_map.csv", "text/csv")
    with col_c:
        st.download_button("Download basic .gdtf", build_simple_gdtf(fixture), "fixtureforge_basic.gdtf", "application/octet-stream")
        st.caption("GDTF export is basic; JSON/CSV are the reliable exports in this build.")

    with st.expander("Raw Fixture JSON"):
        st.json(fixture)
else:
    st.info("Upload a manual, then click Analyze. For B240, the built-in template will load automatically.")
