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
from naming import default_display_names, apply_fixture_names, polish_fixture_labels, clean_filename
from branding import inject_brand_css, render_sidebar_logo, render_hero, section_header


st.set_page_config(
    page_title=APP_NAME,
    page_icon="💜",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_brand_css()

def reset_builder():
    for key in ["fixture", "manual_text", "images"]:
        st.session_state.pop(key, None)
    # Keep upload widget cannot be programmatically cleared, but the state starts fresh.
    st.session_state.fixture = None
    st.session_state.manual_text = ""
    st.session_state.images = []


if "fixture" not in st.session_state:
    st.session_state.fixture = None
if "manual_text" not in st.session_state:
    st.session_state.manual_text = ""
if "images" not in st.session_state:
    st.session_state.images = []

with st.sidebar:
    render_sidebar_logo()
    st.markdown("### Einstellungen")
    st.caption("OpenRouter ist optional. Das B240-Template funktioniert auch ohne KI.")
    model = st.text_input("OpenRouter Modell", value=OPENROUTER_MODEL)
    max_pages = st.slider("Max. PDF-Seiten", 1, 30, 9)
    ocr_lang = st.text_input("OCR Sprache", value="deu+eng")
    if OPENROUTER_API_KEY:
        st.success("OPENROUTER_API_KEY gefunden")
    else:
        st.warning("Kein OpenRouter-Key. B240 Template funktioniert trotzdem.")
    st.divider()
    if st.button("Reset / Neu starten", use_container_width=True):
        reset_builder()
        st.rerun()
    st.caption("Setzt Analyse, Tabellen und Exportdaten zurück.")

render_hero(APP_VERSION)

top_cols = st.columns([1, 0.22])
with top_cols[1]:
    if st.button("Reset", use_container_width=True):
        reset_builder()
        st.rerun()


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


with st.container(border=True):
    section_header(
        1,
        "Manual hochladen",
        "PDF, JPG oder PNG. Bei bildbasierten PDFs kann Tesseract-OCR automatisch mitlaufen.",
    )
    uploaded = st.file_uploader(
        "Manual / DMX-Sheet",
        type=["pdf", "jpg", "jpeg", "png"],
        label_visibility="collapsed",
        help="Manual oder DMX-Tabelle hier ablegen."
    )
    if uploaded:
        st.success(f"Upload erkannt: {uploaded.name} · {uploaded.size/1024:.1f} KB")

    col_left, col_right = st.columns([2.1, 1])
    with col_left:
        extra_context = st.text_area(
            "Optionale Regeln / Kontext",
            placeholder="Beispiel: Eurolite Fixture, bevorzugt 48CH, Köpfe als Head 1–4 darstellen.",
            height=95,
        )
    with col_right:
        st.write("")
        use_b240_template = st.checkbox("B240 Template erzwingen", value=False)
        use_ocr = st.checkbox("OCR nutzen, wenn kein PDF-Text vorhanden ist", value=True)
        use_ai = st.checkbox("OpenRouter KI für generische Analyse nutzen", value=True)

    manual_text_fallback = st.text_area(
        "Fallback: Manual-/OCR-Text einfügen",
        placeholder="Wenn das PDF nur aus Bildern besteht oder du eine Tabelle kopiert hast, Text hier einfügen.",
        height=125,
    )

with st.container(border=True):
    section_header(
        2,
        "Analyse",
        "FixtureForge liest die Datei, erkennt den B240 automatisch oder nutzt OpenRouter für generische Fixtures.",
    )
    if st.button("Analyse starten", type="primary", use_container_width=True):
        try:
            text = ""
            images = []
            if uploaded:
                with st.spinner("Datei wird gelesen..."):
                    text, images = load_file(uploaded)
                    st.session_state.images = images

            if manual_text_fallback.strip():
                text = manual_text_fallback.strip()

            if use_b240_template or looks_like_b240(uploaded.name if uploaded else "", text):
                fixture = polish_fixture_labels(build_b240_fixture())
                fixture = apply_fixture_names(fixture, default_display_names(fixture))
                st.session_state.fixture = fixture
                st.session_state.manual_text = text
                st.success("Eurolite LED TMH Bar B240 erkannt. Template geladen und Namen bereinigt.")
            else:
                if not text.strip() and use_ocr and images:
                    with st.spinner("Kein eingebetteter Text gefunden. Tesseract-OCR läuft..."):
                        text = ocr_images(images, lang=ocr_lang)
                st.session_state.manual_text = text

                if not text.strip():
                    st.warning("Kein Text gefunden. Nutze OCR, füge Text im Fallback-Feld ein oder nutze später ein Vision-Modell.")
                elif use_ai:
                    with st.spinner("OpenRouter analysiert die DMX-Daten..."):
                        raw = analyze_text_with_openrouter(text, model=model, extra_context=extra_context)
                        fixture = polish_fixture_labels(normalize_fixture(raw))
                        fixture = apply_fixture_names(fixture, default_display_names(fixture))
                        st.session_state.fixture = fixture
                    st.success("KI-Analyse abgeschlossen.")
                else:
                    st.info("Text extrahiert. Aktiviere OpenRouter-KI oder nutze ein Template.")
        except Exception as exc:
            st.error(str(exc))
            with st.expander("Debug Traceback"):
                st.code(traceback.format_exc())

if st.session_state.images:
    with st.container(border=True):
        section_header(3, "Vorschau", "Gerenderte PDF-Seiten oder Bildvorschau.")
        with st.expander("Seiten/Bilder anzeigen", expanded=False):
            cols = st.columns(3)
            for idx, (name, img) in enumerate(st.session_state.images[:9]):
                with cols[idx % 3]:
                    st.image(img, caption=name, use_container_width=True)

if st.session_state.manual_text:
    with st.container(border=True):
        section_header(4, "Extrahierter Text", "Textbasis, die für die KI-Analyse verwendet wurde.")
        with st.expander("Text anzeigen", expanded=False):
            st.text_area("Text", st.session_state.manual_text, height=280, label_visibility="collapsed")

fixture = st.session_state.fixture

if fixture:
    with st.container(border=True):
        section_header(5, "Fixture Daten", "Benennung für MA3, Exportdateien und Fixture Library bereinigen.")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Hersteller", fixture.get("manufacturer") or "-")
        with c2:
            st.metric("Fixture", fixture.get("fixture_name") or "-")
        with c3:
            st.metric("Modi", len(fixture.get("modes", [])))

        defaults = default_display_names(fixture)
        n1, n2 = st.columns(2)
        with n1:
            manufacturer = st.text_input("GDTF Manufacturer", fixture.get("manufacturer") or defaults["manufacturer"])
            fixture_name = st.text_input("GDTF Fixture Name", fixture.get("fixture_name") or defaults["fixture_name"])
            short_name = st.text_input("Short Name", fixture.get("short_name") or defaults["short_name"])
        with n2:
            long_name = st.text_input("Long Name", fixture.get("long_name") or defaults["long_name"])
            file_prefix = st.text_input("Export-Dateiname", fixture.get("file_prefix") or defaults["file_prefix"])
            st.caption("Der Dateiname wird automatisch sicher formatiert, z. B. ohne Leerzeichen/Sonderzeichen.")

        fixture = apply_fixture_names(fixture, {
            "manufacturer": manufacturer,
            "fixture_name": fixture_name,
            "short_name": short_name,
            "long_name": long_name,
            "file_prefix": file_prefix,
        })
        st.session_state.fixture = fixture

    with st.container(border=True):
        section_header(6, "Kanäle prüfen", "Modi aufklappen, Kanäle korrigieren und danach exportieren.")
        mode_names = [f"{m.get('name')} · {m.get('channel_count')} CH" for m in fixture.get("modes", [])]
        selected = st.selectbox(
            "Schnellauswahl Modus",
            options=list(range(len(mode_names))),
            format_func=lambda i: mode_names[i] if mode_names else "-",
            index=max(0, len(mode_names)-1)
        )

        for i, mode in enumerate(fixture.get("modes", [])):
            with st.expander(f"{mode.get('name')} · {mode.get('channel_count')} CH", expanded=(i == selected)):
                df = mode_to_dataframe(mode)
                edited = st.data_editor(df, use_container_width=True, num_rows="dynamic", key=f"editor_{i}")
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

    with st.container(border=True):
        section_header(7, "Export", "GDTF für MA3, CSV für Daslight/Wolfmix oder JSON als universelle FixtureForge-Datei.")
        prefix = clean_filename(fixture.get("file_prefix") or "Nachtaktiv_GDTF_Builder")
        e1, e2, e3 = st.columns(3)
        with e1:
            st.download_button(
                "JSON herunterladen",
                fixture_to_json_bytes(fixture),
                f"{prefix}.json",
                "application/json",
                use_container_width=True,
            )
        with e2:
            st.download_button(
                "CSV herunterladen",
                fixture_to_csv_bytes(fixture),
                f"{prefix}_channel_map.csv",
                "text/csv",
                use_container_width=True,
            )
        with e3:
            st.download_button(
                "GDTF herunterladen",
                build_simple_gdtf(fixture),
                f"{prefix}.gdtf",
                "application/octet-stream",
                use_container_width=True,
            )

        with st.expander("Raw Fixture JSON"):
            st.json(fixture)
else:
    with st.container(border=True):
        section_header(3, "Bereit", "Lade ein Manual hoch und starte die Analyse. Beim B240 wird automatisch das Template geladen.")
        st.info("Noch keine Fixture geladen.")

st.markdown('<div class="nas-footer">Nachtaktiv Solutions GmbH · GDTF Builder · FixtureForge Engine</div>', unsafe_allow_html=True)
