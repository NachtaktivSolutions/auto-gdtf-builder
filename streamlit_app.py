from __future__ import annotations
import json, tempfile
from pathlib import Path
import pandas as pd
import streamlit as st
from fixtureforge.ai_extract import extract_fixture_with_gemini
from fixtureforge.schema import Fixture, Channel, ValueRange
from fixtureforge.gdtf_builder import build_gdtf
from fixtureforge.export_csv import fixture_to_channel_csv
from fixtureforge.learning import make_training_record, records_to_jsonl, parse_jsonl, build_knowledge_context
from fixtureforge.gdtf_reference import parse_gdtf_reference

st.set_page_config(page_title="FixtureForge AI", page_icon="💡", layout="wide")
st.title("💡 FixtureForge AI")
st.caption("Manual/DMX-Sheet hochladen → KI erkennt Channels & Values → prüfen/korrigieren → Training speichern → Export")

if "fixture" not in st.session_state:
    st.session_state.fixture = None
if "original" not in st.session_state:
    st.session_state.original = None
if "training_records" not in st.session_state:
    st.session_state.training_records = []

with st.sidebar:
    st.header("Projekt")
    manufacturer_hint = st.text_input("Hersteller Hinweis", "")
    fixture_hint = st.text_input("Modell Hinweis", "")
    model = st.selectbox("KI Modell", ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"], index=0)
    st.divider()
    st.header("Lernen")
    kb_file = st.file_uploader("Trainingsdaten importieren (.jsonl)", type=["jsonl"], key="kb_upload")
    if kb_file is not None and st.button("Trainingsdaten laden"):
        text = kb_file.getvalue().decode("utf-8")
        st.session_state.training_records = parse_jsonl(text)
        st.success(f"{len(st.session_state.training_records)} Trainingsbeispiele geladen.")
    manual_rules = st.text_area(
        "Manuelle Regeln für diese Analyse",
        value="",
        placeholder="Beispiel: Bei Eurolite 'Geschwindigkeit PAN/TILT' immer als PanTiltSpeed mappen. Reset 231-249 als Reset snap=true.",
        height=120,
    )

    st.divider()
    st.header("Referenz-Training")
    st.caption("Hier kannst du eine funktionierende GDTF als Beispiel hochladen. Die App liest daraus Mapping/Attribute und nutzt es beim nächsten KI-Lauf als Kontext.")
    ref_gdtf = st.file_uploader("Funktionierende GDTF hochladen", type=["gdtf"], key="ref_gdtf")
    ref_note = st.text_input("Referenz-Notiz", placeholder="z. B. Eurolite B240 funktionierende 48CH GDTF")
    if ref_gdtf is not None and st.button("GDTF-Referenz als Training merken"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".gdtf") as f:
            f.write(ref_gdtf.getvalue())
            ref_path = f.name
        try:
            ref = parse_gdtf_reference(ref_path)
            st.session_state.training_records.append({
                "type": "gdtf_reference",
                "note": ref_note,
                "gdtf_reference": ref,
            })
            st.success("GDTF-Referenz gespeichert. Sie wird ab der nächsten Analyse als Lernkontext genutzt.")
        except Exception as e:
            st.error(f"GDTF konnte nicht gelesen werden: {e}")

    if st.session_state.training_records:
        st.caption(f"Aktive Trainingsbeispiele: {len(st.session_state.training_records)}")
        st.download_button(
            "Trainingsdaten herunterladen",
            records_to_jsonl(st.session_state.training_records),
            file_name="fixtureforge_training_data.jsonl",
            mime="application/jsonl",
        )
    st.divider()
    st.caption("Export: GDTF ist MVP. Daslight/Wolfmix aktuell als Kanalmap CSV.")

uploaded = st.file_uploader("PDF, JPG oder PNG hochladen", type=["pdf", "jpg", "jpeg", "png"])

if uploaded and st.button("KI Analyse starten", type="primary"):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error("GEMINI_API_KEY fehlt in Streamlit Secrets. In Streamlit: Settings → Secrets → GEMINI_API_KEY eintragen.")
        st.stop()
    suffix = Path(uploaded.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(uploaded.getvalue())
        tmp = f.name
    knowledge_context = build_knowledge_context(st.session_state.training_records, manual_rules)
    with st.spinner("KI analysiert Manual/DMX-Sheet mit Trainingskontext..."):
        try:
            fixture = extract_fixture_with_gemini(api_key, tmp, model=model, knowledge_context=knowledge_context)
            if manufacturer_hint:
                fixture.manufacturer = manufacturer_hint
            if fixture_hint:
                fixture.fixture_name = fixture_hint
            st.session_state.fixture = fixture
            st.session_state.original = fixture.model_dump()
            st.success("Analyse fertig.")
        except Exception as e:
            st.error(str(e))
            st.stop()

fixture: Fixture | None = st.session_state.fixture
if fixture:
    st.subheader("1. Fixture Informationen")
    c1, c2, c3, c4 = st.columns(4)
    fixture.manufacturer = c1.text_input("Hersteller", fixture.manufacturer)
    fixture.fixture_name = c2.text_input("Fixture Name", fixture.fixture_name)
    fixture.short_name = c3.text_input("Short Name", fixture.short_name)
    fixture.beam_angle_deg = c4.number_input("Beam Angle °", value=float(fixture.beam_angle_deg or 0), step=0.5)
    c5, c6 = st.columns(2)
    fixture.pan_deg = c5.number_input("Pan °", value=float(fixture.pan_deg or 0), step=1.0)
    fixture.tilt_deg = c6.number_input("Tilt °", value=float(fixture.tilt_deg or 0), step=1.0)

    st.subheader("2. DMX Mode wählen und Kanäle korrigieren")
    mode_names = [m.name for m in fixture.modes]
    selected_mode = st.selectbox("Mode", mode_names)
    mode = next(m for m in fixture.modes if m.name == selected_mode)

    rows = []
    for ch in sorted(mode.channels, key=lambda x: x.channel):
        rows.append({
            "channel": ch.channel,
            "head": ch.head or "",
            "name": ch.name,
            "attribute": ch.attribute,
            "resolution": ch.resolution,
            "fine_of": ch.fine_of or "",
            "default": ch.default,
            "snap": ch.snap,
            "values": " | ".join(f"{v.from_value}-{v.to_value}: {v.label}" for v in ch.values),
        })
    df = pd.DataFrame(rows)
    edited = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key="channel_editor",
        column_config={
            "attribute": st.column_config.SelectboxColumn(
                "attribute",
                options=["Pan", "PanFine", "Tilt", "TiltFine", "PanTiltSpeed", "Dimmer", "Shutter", "Strobe", "Red", "Green", "Blue", "White", "Amber", "UV", "ColorMacro", "Gobo", "GoboShake", "GoboRotate", "Prism", "PrismRotate", "Zoom", "Focus", "Frost", "Iris", "Macro", "MacroSpeed", "Reset", "Control", "Unknown"],
            ),
            "resolution": st.column_config.SelectboxColumn("resolution", options=["8bit", "coarse", "fine"]),
        },
    )

    if st.button("Korrekturen übernehmen"):
        channels = []
        errors = []
        for idx, r in edited.iterrows():
            vals = []
            for part in str(r.get("values", "")).split("|"):
                part = part.strip()
                if not part:
                    continue
                try:
                    rng, label = part.split(":", 1)
                    a, b = rng.strip().split("-", 1)
                    vals.append(ValueRange(from_value=int(a), to_value=int(b), label=label.strip()))
                except Exception:
                    errors.append(f"Zeile {idx+1}: Value-Format ungültig: {part}")
            try:
                channels.append(Channel(
                    channel=int(r["channel"]),
                    head=int(r["head"]) if str(r["head"]).strip() else None,
                    name=str(r["name"]),
                    attribute=str(r["attribute"]),
                    resolution=str(r["resolution"]),
                    fine_of=int(r["fine_of"]) if str(r["fine_of"]).strip() else None,
                    default=int(r["default"]),
                    snap=bool(r["snap"]),
                    values=vals,
                ))
            except Exception as e:
                errors.append(f"Zeile {idx+1}: {e}")
        if errors:
            st.error("\n".join(errors))
        else:
            mode.channels = channels
            mode.channel_count = max([c.channel for c in channels] or [mode.channel_count])
            st.success("Korrekturen übernommen.")

    st.subheader("3. Lernen")
    st.info("Das ist Prompt-Training: Deine bestätigten Korrekturen werden als JSONL gespeichert und bei künftigen Analysen als Lernkontext mitgegeben. Echtes Fine-Tuning machen wir später, wenn genug geprüfte Beispiele vorhanden sind.")
    note = st.text_input("Notiz zur Korrektur / Herstellerregel")
    if st.button("Korrektur als Trainingsdaten merken"):
        record = make_training_record(st.session_state.original or {}, fixture, note)
        st.session_state.training_records.append(record)
        st.success("Korrektur im aktuellen Trainingsspeicher gemerkt. Bitte danach Trainingsdaten herunterladen.")
    if st.session_state.training_records:
        st.download_button(
            "Trainingsdaten jetzt herunterladen (.jsonl)",
            records_to_jsonl(st.session_state.training_records),
            file_name="fixtureforge_training_data.jsonl",
            mime="application/jsonl",
            type="primary",
        )

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
