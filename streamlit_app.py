from __future__ import annotations

import json
import traceback
from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st

from config import APP_NAME, APP_VERSION, DEFAULT_OPENROUTER_MODEL, OPENROUTER_API_KEY
from parser_pdf import pdf_to_page_images, image_file_to_png_bytes
from providers_openrouter import analyze_images_with_openrouter, OpenRouterError
from models_fixture import normalize_fixture, fixture_to_json_bytes
from exporters_csv import mode_to_dataframe, fixture_to_csv_bytes
from exporters_gdtf import build_basic_gdtf


st.set_page_config(page_title=APP_NAME, page_icon="💡", layout="wide")

st.title(f"💡 {APP_NAME}")
st.caption(f"v{APP_VERSION} · OpenRouter only · Gemini removed")

with st.sidebar:
    st.header("Settings")
    st.write("Provider: **OpenRouter**")
    model = st.text_input("Model", value=DEFAULT_OPENROUTER_MODEL)
    max_pdf_pages = st.slider("Max PDF pages sent to AI", 1, 20, 9)
    st.info("Streamlit Secret required: OPENROUTER_API_KEY")
    if OPENROUTER_API_KEY:
        st.success("OPENROUTER_API_KEY found")
    else:
        st.error("OPENROUTER_API_KEY missing")

st.subheader("1) Upload Manual / DMX Sheet")
uploaded = st.file_uploader(
    "PDF, JPG, JPEG or PNG",
    type=["pdf", "jpg", "jpeg", "png"],
    accept_multiple_files=False,
)

extra_context = st.text_area(
    "Optional context / rules",
    placeholder="Example: This is a Eurolite fixture. Prefer 48CH mode. Build multi-instance if possible.",
    height=90,
)

if "fixture" not in st.session_state:
    st.session_state.fixture = None
if "images_preview" not in st.session_state:
    st.session_state.images_preview = []

def prepare_images(uploaded_file) -> List[Tuple[str, bytes]]:
    raw = uploaded_file.getvalue()
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return pdf_to_page_images(raw, max_pages=max_pdf_pages)
    return [(uploaded_file.name, image_file_to_png_bytes(raw))]

if uploaded:
    st.write(f"Uploaded: `{uploaded.name}` · {uploaded.size/1024:.1f} KB")

    if st.button("Analyze with OpenRouter", type="primary"):
        try:
            with st.spinner("Preparing pages/images..."):
                images = prepare_images(uploaded)
                st.session_state.images_preview = images

            st.info(f"Prepared {len(images)} image page(s) for AI analysis.")

            with st.spinner("OpenRouter AI is analyzing the DMX chart..."):
                raw_result = analyze_images_with_openrouter(
                    images=images,
                    model=model,
                    extra_context=extra_context,
                    timeout_seconds=120,
                )
                fixture = normalize_fixture(raw_result)
                st.session_state.fixture = fixture

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

fixture = st.session_state.fixture

if fixture:
    st.subheader("2) Universal Fixture JSON")
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

    edited_modes = []
    for mi, mode in enumerate(fixture.get("modes", [])):
        with st.expander(f"Mode: {mode.get('name')} · {mode.get('channel_count')} CH", expanded=(mi == 0)):
            df = mode_to_dataframe(mode)
            if df.empty:
                st.warning("No channels detected in this mode.")
                edited_modes.append(mode)
                continue
            edited_df = st.data_editor(
                df,
                num_rows="dynamic",
                use_container_width=True,
                key=f"mode_editor_{mi}",
            )
            # Keep simplified edited table back into fixture.
            channels = []
            for _, row in edited_df.iterrows():
                try:
                    ch_no = int(row.get("channel"))
                except Exception:
                    continue
                channels.append({
                    "channel": ch_no,
                    "fine_channel": None if pd.isna(row.get("fine_channel")) or row.get("fine_channel") == "" else int(float(row.get("fine_channel"))),
                    "attribute": str(row.get("attribute") or "Unknown"),
                    "raw_label": str(row.get("raw_label") or ""),
                    "raw_description": str(row.get("raw_description") or ""),
                    "geometry": None if pd.isna(row.get("geometry")) else str(row.get("geometry") or ""),
                    "default_value": None,
                    "highlight_value": None,
                    "ranges": mode.get("channels", [])[0].get("ranges", []) if False else [],
                })
            mode["channels"] = channels
            edited_modes.append(mode)
    fixture["modes"] = edited_modes

    st.subheader("4) Export")
    export_format = st.selectbox("Format", ["GDTF", "Daslight/Wolfmix CSV", "Universal Fixture JSON"])

    if export_format == "GDTF":
        gdtf_bytes = build_basic_gdtf(fixture)
        st.download_button(
            "Download .gdtf",
            data=gdtf_bytes,
            file_name=f"{fixture.get('manufacturer') or 'Unknown'}_{fixture.get('fixture_name') or 'Fixture'}.gdtf".replace(" ", "_"),
            mime="application/octet-stream",
        )
        st.caption("v0.4 creates a basic GDTF skeleton. Full GDTF logic will be improved in v0.5/v0.6.")
    elif export_format == "Daslight/Wolfmix CSV":
        csv_bytes = fixture_to_csv_bytes(fixture)
        st.download_button(
            "Download CSV",
            data=csv_bytes,
            file_name=f"{fixture.get('manufacturer') or 'Unknown'}_{fixture.get('fixture_name') or 'Fixture'}_channel_map.csv".replace(" ", "_"),
            mime="text/csv",
        )
    else:
        st.download_button(
            "Download JSON",
            data=fixture_to_json_bytes(fixture),
            file_name=f"{fixture.get('manufacturer') or 'Unknown'}_{fixture.get('fixture_name') or 'Fixture'}.json".replace(" ", "_"),
            mime="application/json",
        )

    with st.expander("Raw Fixture JSON"):
        st.json(fixture)
else:
    st.info("Upload a manual or DMX chart and click Analyze.")
