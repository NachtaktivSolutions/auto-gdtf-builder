from __future__ import annotations

import traceback
import pandas as pd
import streamlit as st

from config import APP_NAME, APP_VERSION, DEFAULT_OPENROUTER_MODEL, OPENROUTER_API_KEY
from ocr_tools import prepare_images, ocr_images
from providers_openrouter import analyze_ocr_text_with_openrouter
from models_fixture import normalize_fixture, fixture_to_json_bytes
from exporters_csv import mode_to_dataframe, fixture_to_csv_bytes
from exporters_gdtf import build_basic_gdtf


st.set_page_config(page_title=APP_NAME, page_icon="💡", layout="wide")
st.title(f"💡 {APP_NAME}")
st.caption(f"v{APP_VERSION} · Local OCR → OpenRouter text model · no Vision model needed")

with st.sidebar:
    st.header("Settings")
    st.write("Provider: **OpenRouter**")
    model = st.text_input("Model", value=DEFAULT_OPENROUTER_MODEL)
    max_pdf_pages = st.slider("Max PDF pages for OCR", 1, 20, 9)
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

if "fixture" not in st.session_state:
    st.session_state.fixture = None
if "ocr_text" not in st.session_state:
    st.session_state.ocr_text = ""
if "images_preview" not in st.session_state:
    st.session_state.images_preview = []

if uploaded:
    st.write(f"Uploaded: `{uploaded.name}` · {uploaded.size/1024:.1f} KB")

    if st.button("OCR + Analyze with OpenRouter", type="primary"):
        try:
            with st.spinner("Preparing pages/images..."):
                images = prepare_images(uploaded, max_pages=max_pdf_pages)
                st.session_state.images_preview = images
            st.info(f"Prepared {len(images)} page/image(s) for local OCR.")

            with st.spinner("Running local OCR... first run can take a bit because OCR model loads."):
                ocr_text = ocr_images(images)
                st.session_state.ocr_text = ocr_text

            if not ocr_text.strip():
                st.error("OCR produced no text. Try a clearer image/PDF or fewer larger pages.")
            else:
                st.success(f"OCR extracted {len(ocr_text)} characters.")

                with st.spinner("OpenRouter text model is mapping OCR text to Fixture JSON..."):
                    raw = analyze_ocr_text_with_openrouter(
                        ocr_text=ocr_text,
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

if st.session_state.images_preview:
    with st.expander("Preview converted pages/images"):
        cols = st.columns(3)
        for idx, (name, img) in enumerate(st.session_state.images_preview[:9]):
            with cols[idx % 3]:
                st.image(img, caption=name, use_container_width=True)

if st.session_state.ocr_text:
    with st.expander("OCR text"):
        st.text_area("Extracted OCR text", st.session_state.ocr_text, height=350)

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
            # Minimal writeback
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
        st.caption("GDTF skeleton is still basic in v0.5. Full GDTF exporter comes next.")

    with st.expander("Raw Fixture JSON"):
        st.json(fixture)
else:
    st.info("Upload a manual or DMX chart, then click OCR + Analyze.")
