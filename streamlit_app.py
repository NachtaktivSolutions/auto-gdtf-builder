import json
import os
from copy import deepcopy

import pandas as pd
import streamlit as st

from ai_extract import extract_fixture_json
from daslight_builder import build_daslight_wolfmix_placeholder
from gdtf_builder import build_channel_csv, build_gdtf
from learning import make_learning_record

st.set_page_config(page_title="Auto GDTF Builder", page_icon="💡", layout="wide")

st.title("💡 Auto GDTF Builder")
st.caption("Manual oder DMX-Sheet hochladen → KI erkennt Kanäle & Values → prüfen/korrigieren → Export")

APP_PASSWORD = st.secrets.get("APP_PASSWORD", "") if hasattr(st, "secrets") else ""
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""

if APP_PASSWORD:
    pw = st.text_input("Passwort", type="password")
    if pw != APP_PASSWORD:
        st.stop()

with st.sidebar:
    st.header("Workflow")
    st.write("1. PDF/Bild hochladen")
    st.write("2. KI analysieren lassen")
    st.write("3. Tabelle korrigieren")
    st.write("4. Format wählen")
    st.write("5. Datei exportieren")
    st.divider()
    model = st.selectbox("KI-Modell", ["gemini-1.5-flash", "gemini-1.5-pro"], index=0)
    st.caption("Flash ist schneller/kostenärmer. Pro ist besser bei schwierigen Manuals.")

uploaded = st.file_uploader("PDF, JPG oder PNG hochladen", type=["pdf", "jpg", "jpeg", "png", "webp"])

col_a, col_b = st.columns(2)
with col_a:
    manufacturer_override = st.text_input("Hersteller optional", placeholder="z. B. Eurolite")
with col_b:
    fixture_override = st.text_input("Modell optional", placeholder="z. B. LED TMH Bar B240")

if "fixture_json" not in st.session_state:
    st.session_state.fixture_json = None
if "original_fixture_json" not in st.session_state:
    st.session_state.original_fixture_json = None

if uploaded and st.button("🤖 KI analysieren", type="primary"):
    with st.spinner("KI liest Manual/DMX-Sheet... das kann etwas dauern"):
        try:
            data = extract_fixture_json(uploaded, GEMINI_API_KEY, model_name=model)
            if manufacturer_override:
                data["manufacturer"] = manufacturer_override
            if fixture_override:
                data["fixture_name"] = fixture_override
            st.session_state.fixture_json = data
            st.session_state.original_fixture_json = deepcopy(data)
            st.success("Analyse fertig. Bitte Tabelle prüfen und bei Bedarf korrigieren.")
        except Exception as e:
            st.error(f"Analyse fehlgeschlagen: {e}")

fixture = st.session_state.fixture_json

if fixture:
    st.subheader("1) Erkannte Fixture-Daten")
    c1, c2, c3 = st.columns(3)
    fixture["manufacturer"] = c1.text_input("Manufacturer", value=fixture.get("manufacturer", ""))
    fixture["fixture_name"] = c2.text_input("Fixture", value=fixture.get("fixture_name", ""))
    fixture["notes"] = c3.text_input("Notizen", value=fixture.get("notes", ""))

    modes = fixture.get("modes", [])
    if not modes:
        st.warning("Keine DMX-Modi erkannt.")
        st.stop()

    mode_names = [m.get("mode_name", f"Mode {i}") for i, m in enumerate(modes)]
    selected_mode_name = st.selectbox("DMX-Modus zum Bearbeiten", mode_names)
    mode_index = mode_names.index(selected_mode_name)
    mode = modes[mode_index]

    st.subheader("2) Übersicht prüfen und korrigieren")
    rows = []
    for ch in mode.get("channels", []):
        ranges = "; ".join([f"{r.get('from')}-{r.get('to')}: {r.get('name')}" for r in ch.get("ranges", [])])
        rows.append({
            "channel": ch.get("channel"),
            "fixture_part": ch.get("fixture_part", ""),
            "raw_name": ch.get("raw_name", ""),
            "attribute": ch.get("attribute", ""),
            "resolution": ch.get("resolution", ""),
            "fine_for_channel": ch.get("fine_for_channel"),
            "default_dmx": ch.get("default_dmx"),
            "highlight_dmx": ch.get("highlight_dmx"),
            "ranges": ranges,
        })
    df = pd.DataFrame(rows)
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, height=420)

    # write edited table back to selected mode
    new_channels = []
    for _, row in edited.iterrows():
        ranges = []
        for part in str(row.get("ranges") or "").split(";"):
            part = part.strip()
            if not part:
                continue
            try:
                left, name = part.split(":", 1)
                start, end = left.strip().split("-", 1)
                ranges.append({"from": int(start), "to": int(end), "name": name.strip(), "type": "step", "comment": ""})
            except Exception:
                ranges.append({"from": 0, "to": 255, "name": part, "type": "unknown", "comment": "parse_warning"})
        try:
            channel_number = int(row.get("channel"))
        except Exception:
            continue
        new_channels.append({
            "channel": channel_number,
            "fixture_part": row.get("fixture_part") or "Base",
            "raw_name": row.get("raw_name") or row.get("attribute") or "Unknown",
            "attribute": row.get("attribute") or "Unknown",
            "resolution": row.get("resolution") or "8bit",
            "fine_for_channel": None if pd.isna(row.get("fine_for_channel")) or row.get("fine_for_channel") in ("", None) else int(row.get("fine_for_channel")),
            "default_dmx": 0 if pd.isna(row.get("default_dmx")) or row.get("default_dmx") in ("", None) else int(row.get("default_dmx")),
            "highlight_dmx": None if pd.isna(row.get("highlight_dmx")) or row.get("highlight_dmx") in ("", None) else int(row.get("highlight_dmx")),
            "ranges": ranges or [{"from": 0, "to": 255, "name": row.get("raw_name") or "Unknown", "type": "continuous", "comment": ""}],
        })
    fixture["modes"][mode_index]["channels"] = new_channels

    st.subheader("3) Exportformat wählen")
    export_format = st.radio("Format", ["GDTF", "Daslight/Wolfmix"], horizontal=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if export_format == "GDTF":
            gdtf = build_gdtf(fixture)
            st.download_button("⬇️ GDTF exportieren", data=gdtf, file_name=f"{fixture.get('manufacturer','Unknown')}@{fixture.get('fixture_name','Fixture')}.gdtf".replace(" ", "_"), mime="application/zip")
        else:
            dl = build_daslight_wolfmix_placeholder(fixture)
            st.download_button("⬇️ Daslight/Wolfmix Map exportieren", data=dl, file_name=f"{fixture.get('manufacturer','Unknown')}_{fixture.get('fixture_name','Fixture')}_daslight_wolfmix_map.csv".replace(" ", "_"), mime="text/csv")
    with col2:
        csv_bytes = build_channel_csv(fixture)
        st.download_button("⬇️ Kanalmap CSV", data=csv_bytes, file_name="channel_map.csv", mime="text/csv")
    with col3:
        learning = make_learning_record(st.session_state.original_fixture_json or {}, fixture)
        st.download_button("🧠 Korrektur als Trainingsdaten", data=learning, file_name="learning_correction.json", mime="application/json")

    with st.expander("Debug JSON anzeigen"):
        st.json(fixture)
else:
    st.info("Lade ein Manual oder ein Bild vom DMX-Sheet hoch und klicke auf KI analysieren.")

st.divider()
st.caption("MVP Hinweis: GDTF-Export ist Best-Effort und sollte in GDTF Builder / grandMA3 getestet werden. Daslight/Wolfmix ist zunächst eine saubere Kanalmap für den manuellen Fixture-Aufbau; nativer Export kann später ergänzt werden.")
