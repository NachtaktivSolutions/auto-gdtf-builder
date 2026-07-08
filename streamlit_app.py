from __future__ import annotations
import json, tempfile
from pathlib import Path
import pandas as pd
import streamlit as st
from fixtureforge.ai_extract import extract_fixture_with_gemini
from fixtureforge.schema import Fixture, Mode, Channel, ValueRange
from fixtureforge.gdtf_builder import build_gdtf
from fixtureforge.export_csv import fixture_to_channel_csv
from fixtureforge.learning import save_training_example

st.set_page_config(page_title="FixtureForge AI", page_icon="💡", layout="wide")
st.title("💡 FixtureForge AI")
st.caption("Manual/DMX-Sheet hochladen → KI erkennt Channels & Values → prüfen/korrigieren → Export")

with st.sidebar:
    st.header("Projekt")
    manufacturer_hint = st.text_input("Hersteller Hinweis", "")
    fixture_hint = st.text_input("Modell Hinweis", "")
    model = st.selectbox("KI Modell", ["gemini-2.0-flash", "gemini-1.5-flash"], index=0)
    st.divider()
    st.caption("Export: GDTF ist MVP. Daslight/Wolfmix aktuell als Kanalmap CSV.")

uploaded = st.file_uploader("PDF, JPG oder PNG hochladen", type=["pdf", "jpg", "jpeg", "png"])
if "fixture" not in st.session_state:
    st.session_state.fixture = None
    st.session_state.original = None

if uploaded and st.button("KI Analyse starten", type="primary"):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error("GEMINI_API_KEY fehlt in Streamlit Secrets.")
        st.stop()
    suffix = Path(uploaded.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(uploaded.getvalue())
        tmp = f.name
    with st.spinner("KI analysiert Manual/DMX-Sheet..."):
        fixture = extract_fixture_with_gemini(api_key, tmp, model=model)
        if manufacturer_hint: fixture.manufacturer = manufacturer_hint
        if fixture_hint: fixture.fixture_name = fixture_hint
        st.session_state.fixture = fixture
        st.session_state.original = fixture.model_dump()
    st.success("Analyse fertig.")

fixture: Fixture | None = st.session_state.fixture
if fixture:
    st.subheader("1. Fixture Informationen")
    c1,c2,c3,c4 = st.columns(4)
    fixture.manufacturer = c1.text_input("Hersteller", fixture.manufacturer)
    fixture.fixture_name = c2.text_input("Fixture Name", fixture.fixture_name)
    fixture.short_name = c3.text_input("Short Name", fixture.short_name)
    fixture.beam_angle_deg = c4.number_input("Beam Angle °", value=float(fixture.beam_angle_deg or 0), step=0.5)
    c5,c6 = st.columns(2)
    fixture.pan_deg = c5.number_input("Pan °", value=float(fixture.pan_deg or 0), step=1.0)
    fixture.tilt_deg = c6.number_input("Tilt °", value=float(fixture.tilt_deg or 0), step=1.0)

    st.subheader("2. DMX Mode wählen und Kanäle korrigieren")
    mode_names = [m.name for m in fixture.modes]
    selected_mode = st.selectbox("Mode", mode_names)
    mode = next(m for m in fixture.modes if m.name == selected_mode)

    rows = []
    for ch in sorted(mode.channels, key=lambda x: x.channel):
        rows.append({
            "channel": ch.channel, "head": ch.head or "", "name": ch.name,
            "attribute": ch.attribute, "resolution": ch.resolution, "fine_of": ch.fine_of or "",
            "default": ch.default, "snap": ch.snap,
            "values": " | ".join(f"{v.from_value}-{v.to_value}: {v.label}" for v in ch.values)
        })
    df = pd.DataFrame(rows)
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="channel_editor")

    if st.button("Korrekturen übernehmen"):
        channels = []
        for _, r in edited.iterrows():
            vals = []
            for part in str(r.get("values", "")).split("|"):
                part = part.strip()
                if not part or ":" not in part or "-" not in part: continue
                rng, label = part.split(":",1)
                a,b = rng.strip().split("-",1)
                vals.append(ValueRange(from_value=int(a), to_value=int(b), label=label.strip()))
            channels.append(Channel(
                channel=int(r["channel"]), head=int(r["head"]) if str(r["head"]).strip() else None,
                name=str(r["name"]), attribute=str(r["attribute"]), resolution=str(r["resolution"]),
                fine_of=int(r["fine_of"]) if str(r["fine_of"]).strip() else None,
                default=int(r["default"]), snap=bool(r["snap"]), values=vals
            ))
        mode.channels = channels
        mode.channel_count = max([c.channel for c in channels] or [mode.channel_count])
        st.success("Korrekturen übernommen.")

    st.subheader("3. Lernen")
    note = st.text_input("Notiz zur Korrektur / Herstellerregel")
    if st.button("Korrektur als Trainingsdaten speichern"):
        path = save_training_example(st.session_state.original or {}, fixture, note)
        st.success(f"Trainingsdaten gespeichert: {path}")

    st.subheader("4. Export")
    export_format = st.radio("Format", ["GDTF", "Daslight/Wolfmix CSV"], horizontal=True)
    safe = f"{fixture.manufacturer}_{fixture.fixture_name}_{selected_mode}".replace(" ", "_").replace("/", "-")
    if export_format == "GDTF":
        data = build_gdtf(fixture, selected_mode)
        st.download_button("GDTF herunterladen", data, file_name=f"{safe}.gdtf", mime="application/octet-stream")
    else:
        data = fixture_to_channel_csv(fixture, selected_mode)
        st.download_button("CSV herunterladen", data, file_name=f"{safe}_channelmap.csv", mime="text/csv")

    with st.expander("Debug JSON anzeigen"):
        st.json(fixture.model_dump())
else:
    st.info("Lade ein Manual oder DMX-Sheet hoch und starte die KI-Analyse.")
