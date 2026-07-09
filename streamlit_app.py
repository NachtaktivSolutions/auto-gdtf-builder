from __future__ import annotations

import traceback
import pandas as pd
import streamlit as st

from config import APP_NAME, APP_VERSION, DEFAULT_OPENROUTER_MODEL, OPENROUTER_API_KEY
from pdf_parser import extract_pdf_text, pdf_to_page_images, image_file_to_preview_bytes
from providers_openrouter import analyze_text_with_openrouter
from models_fixture import normalize_fixture, fixture_to_json_bytes
from exporters_csv import mode_to_dataframe, fixture_to_csv_bytes
from exporters_gdtf import build_basic_gdtf


st.set_page_config(page_title=APP_NAME, page_icon="💡", layout="wide")
st.title(f"💡 {APP_NAME}")
st.caption(f"v{APP_VERSION} · Parser-first · no Gemini · no OpenCV/RapidOCR")

with st.sidebar:
    st.header("Settings")
    st.write("Provider: **OpenRouter**")
    model = st.text_input("Model", value=DEFAULT_OPENROUTER_MODEL)
    max_pdf_pages = st.slider("Max PDF pages", 1, 40, 20)
    st.info("Required Streamlit Secret: OPENROUTER_API_KEY")
    st.success("OPENROUTER_API_KEY found") if OPENROUTER_API_KEY else st.error("OPENROUTER_API_KEY missing")
    st.caption("Recommended: mistralai/mistral-small-3.2-24b-instruct:free")

st.subheader("1) Upload Manual / DMX Sheet")
uploaded = st.file_uploader("PDF, JPG, JPEG or PNG", type=["pdf", "jpg", "jpeg", "png"])
extra_context = st.text_area(
    "Optional context / rules",
    placeholder="Example: This is a Eurolite fixture. Prefer 48CH mode. Build multi-instance if possible.",
    height=90,
)

manual_text_fallback = st.text_area(
    "Fallback: paste manual/OCR text here",
    placeholder="If your PDF is image-only and no text can be extracted, paste copied/OCR text here.",
    height=180,
)

if "fixture" not in st.session_state:
    st.session_state.fixture = None
if "manual_text" not in st.session_state:
    st.session_state.manual_text = ""
if "previews" not in st.session_state:
    st.session_state.previews = []

def get_text_and_previews(uploaded_file):
    if uploaded_file is None:
        return "", []
    raw = uploaded_file.getvalue()
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        text = extract_pdf_text(raw, max_pages=max_pdf_pages)
        previews = pdf_to_page_images(raw, max_pages=min(9, max_pdf_pages))
        return text, previews
    preview = image_file_to_preview_bytes(raw)
    return "", [(uploaded_file.name, preview)]

if uploaded:
    st.write(f"Uploaded: `{uploaded.name}` · {uploaded.size/1024:.1f} KB")

if st.button("Extract text / Analyze", type="primary"):
    try:
        text_from_file = ""
        previews = []
        if uploaded:
            with st.spinner("Extracting PDF text / preparing preview..."):
                text_from_file, previews = get_text_and_previews(uploaded)
                st.session_state.previews = previews

        manual_text = (manual_text_fallback or "").strip() or text_from_file.strip()
        st.session_state.manual_text = manual_text

        if not manual_text:
            st.warning("No embedded text found. This is probably an image-only/scanned PDF. Use the fallback text field for now.")
        else:
            st.success(f"Using {len(manual_text)} characters of manual text.")
            with st.spinner("OpenRouter text model is mapping text to Fixture JSON..."):
                raw = analyze_text_with_openrouter(
                    manual_text=manual_text,
                    model=model,
                    extra_context=extra_context,
                    timeout_seconds=120,
                )
                st.session_state.fixture = normalize_fixture(raw)
            st.success("Analysis complete.")
    except Exception as exc:
        st.error(str(exc))
        with st.expander("Debug traceback"):
            st.code(traceback.format_exc())

if st.session_state.previews:
    with st.expander("Page/image preview"):
        cols = st.columns(3)
        for idx, (name, img) in enumerate(st.session_state.previews[:9]):
            with cols[idx % 3]:
                st.image(img, caption=name, use_container_width=True)

if st.session_state.manual_text:
    with st.expander("Manual text used for AI"):
        st.text_area("Text", st.session_state.manual_text, height=350)

fixture = st.session_state.fixture

if fixture:
    st.subheader("2) Fixture Info")
    col1, col2, col3 = st.columns(3)
    with col1:
        fixture["manufacturer"] = st.text_input("Manufacturer", fixture.get("manufacturer") or "")
    with col2:
        fixture["fixture_name"] = st.text_input("Fixture name", fixture.get("fixture_name") or "")
    with col3:
        st.metric("Modes detected", len(fixture.get("modes", [])))

    if fixture.get("warnings"):
        with st.expander("Warnings"):
            for w in fixture["warnings"]:
                st.warning(w)

    st.subheader("3) Review / Edit Channels")
    for mi, mode in enumerate(fixture.get("modes", [])):
        with st.expander(f"Mode: {mode.get('name')} · {mode.get('channel_count')} CH", expanded=(mi == 0)):
            df = mode_to_dataframe(mode)
            if df.empty:
                st.warning("No channels detected in this mode.")
                continue
            edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key=f"mode_{mi}")
            new_channels = []
            for _, row in edited_df.iterrows():
                try:
                    ch_no = int(row.get("channel"))
                except Exception:
                    continue
                fine = row.get("fine_channel")
                try:
                    fine = None if pd.isna(fine) or fine == "" else int(float(fine))
                except Exception:
                    fine = None
                new_channels.append({
                    "channel": ch_no,
                    "fine_channel": fine,
                    "attribute": str(row.get("attribute") or "Unknown"),
                    "raw_label": str(row.get("raw_label") or ""),
                    "raw_description": str(row.get("raw_description") or ""),
                    "geometry": None if pd.isna(row.get("geometry")) else str(row.get("geometry") or ""),
                    "default_value": None,
                    "highlight_value": None,
                    "ranges": [],
                })
            mode["channels"] = new_channels

    st.subheader("4) Export")
    export_format = st.selectbox("Format", ["Universal Fixture JSON", "Daslight/Wolfmix CSV", "GDTF skeleton"])

    if export_format == "Universal Fixture JSON":
        st.download_button("Download JSON", fixture_to_json_bytes(fixture), "fixtureforge_fixture.json", "application/json")
    elif export_format == "Daslight/Wolfmix CSV":
        st.download_button("Download CSV", fixture_to_csv_bytes(fixture), "fixtureforge_channel_map.csv", "text/csv")
    else:
        st.download_button("Download .gdtf", build_basic_gdtf(fixture), "fixtureforge_basic.gdtf", "application/octet-stream")
        st.caption("GDTF skeleton is still basic in v0.6. Full GDTF exporter comes next.")

    with st.expander("Raw Fixture JSON"):
        st.json(fixture)
else:
    st.info("Upload a text-based PDF or paste manual/OCR text, then click Analyze.")
