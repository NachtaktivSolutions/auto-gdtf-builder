import json
from copy import deepcopy

import pandas as pd
import streamlit as st

from ai_extract import extract_fixture_with_gemini
from gdtf_builder import build_channel_csv, build_gdtf_package, validate_fixture_json

st.set_page_config(page_title="Auto GDTF Generator", page_icon="💡", layout="wide")


def get_secret(name: str, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


def require_password():
    app_password = get_secret("APP_PASSWORD", "")
    if not app_password:
        st.warning("APP_PASSWORD ist noch nicht gesetzt. Die App ist aktuell ohne Passwort offen.")
        return True
    if st.session_state.get("auth_ok"):
        return True
    st.title("🔐 Auto GDTF Generator")
    pwd = st.text_input("Passwort", type="password")
    if st.button("Einloggen"):
        if pwd == app_password:
            st.session_state["auth_ok"] = True
            st.rerun()
        else:
            st.error("Falsches Passwort")
    return False


def normalize_mime(uploaded_file) -> str:
    mime = uploaded_file.type or "application/octet-stream"
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return "application/pdf"
    if name.endswith(".png"):
        return "image/png"
    if name.endswith(".jpg") or name.endswith(".jpeg"):
        return "image/jpeg"
    if name.endswith(".webp"):
        return "image/webp"
    return mime


def mode_to_df(mode):
    rows = []
    for ch in mode.get("channels", []):
        ranges = ch.get("ranges") or []
        ranges_text = " | ".join([f"{r.get('from')}-{r.get('to')}: {r.get('name')}" for r in ranges])
        rows.append({
            "channel": ch.get("channel"),
            "fine_channel": ch.get("fine_channel"),
            "geometry": ch.get("geometry"),
            "attribute": ch.get("attribute"),
            "function": ch.get("function"),
            "default": ch.get("default"),
            "ranges": ranges_text,
        })
    return pd.DataFrame(rows)


def parse_ranges(text):
    ranges = []
    if not text:
        return [{"from": 0, "to": 255, "name": "Full"}]
    for part in str(text).split("|"):
        part = part.strip()
        if not part:
            continue
        if ":" in part:
            rng, name = part.split(":", 1)
        else:
            rng, name = part, part
        if "-" in rng:
            fr, to = rng.split("-", 1)
        else:
            fr, to = "0", "255"
        try:
            ranges.append({"from": int(fr.strip()), "to": int(to.strip()), "name": name.strip()})
        except Exception:
            ranges.append({"from": 0, "to": 255, "name": part})
    return ranges or [{"from": 0, "to": 255, "name": "Full"}]


def df_to_mode(original_mode, df):
    mode = deepcopy(original_mode)
    channels = []
    for _, row in df.iterrows():
        try:
            channel = int(row["channel"])
        except Exception:
            continue
        fine = row.get("fine_channel")
        try:
            fine = int(fine) if pd.notna(fine) and str(fine).strip() != "" else None
        except Exception:
            fine = None
        default = row.get("default")
        try:
            default = int(default) if pd.notna(default) and str(default).strip() != "" else None
        except Exception:
            default = None
        channels.append({
            "channel": channel,
            "geometry": str(row.get("geometry") or "Base"),
            "attribute": str(row.get("attribute") or "Unknown"),
            "function": str(row.get("function") or row.get("attribute") or "Unknown"),
            "resolution": "16bit" if fine else "8bit",
            "fine_channel": fine,
            "default": default,
            "ranges": parse_ranges(row.get("ranges")),
        })
    mode["channels"] = channels
    return mode


if not require_password():
    st.stop()

st.title("💡 Auto GDTF Generator")
st.caption("MVP: Manual/DMX-Sheet hochladen → KI extrahiert Kanalmap → Review → .gdtf Download")

with st.sidebar:
    st.header("Einstellungen")
    model = st.text_input("Gemini Modell", value="gemini-3.5-flash")
    st.markdown("Secrets in Streamlit:")
    st.code('GEMINI_API_KEY = "..."\nAPP_PASSWORD = "..."', language="toml")
    if st.button("Session leeren"):
        st.session_state.clear()
        st.rerun()

col_a, col_b, col_c = st.columns(3)
with col_a:
    manufacturer_hint = st.text_input("Hersteller", placeholder="z. B. Eurolite")
with col_b:
    model_hint = st.text_input("Modell", placeholder="z. B. LED TMH Bar B240")
with col_c:
    mode_hint = st.text_input("Fokus / DMX-Modus", value="alle Modi")

uploaded = st.file_uploader("Manual oder DMX-Sheet hochladen", type=["pdf", "png", "jpg", "jpeg", "webp"])

if uploaded:
    st.info(f"Datei geladen: {uploaded.name} ({uploaded.size / 1024:.1f} KB)")

    if st.button("🔎 KI analysieren", type="primary"):
        with st.spinner("KI liest Manual/DMX-Sheet und extrahiert Kanalmap..."):
            try:
                data = extract_fixture_with_gemini(
                    uploaded.getvalue(),
                    normalize_mime(uploaded),
                    uploaded.name,
                    manufacturer_hint=manufacturer_hint,
                    model_hint=model_hint,
                    mode_hint=mode_hint,
                    model=model,
                )
                st.session_state["fixture_json"] = data
                st.success("Analyse fertig")
            except Exception as e:
                st.error(str(e))
                st.stop()

fixture = st.session_state.get("fixture_json")
if fixture:
    st.subheader("1) Erkannte Fixture-Daten")
    c1, c2, c3 = st.columns(3)
    with c1:
        fixture["manufacturer"] = st.text_input("Manufacturer", value=fixture.get("manufacturer") or manufacturer_hint or "Unknown")
    with c2:
        fixture["fixture_name"] = st.text_input("Fixture Name", value=fixture.get("fixture_name") or model_hint or "Generated Fixture")
    with c3:
        fixture["short_name"] = st.text_input("Short Name", value=fixture.get("short_name") or fixture.get("fixture_name", "Fixture")[:16])

    notes = fixture.get("notes") or []
    if notes:
        with st.expander("KI-Notizen"):
            for note in notes:
                st.write("-", note)

    warnings = validate_fixture_json(fixture)
    if warnings:
        with st.expander("⚠️ Plausibilitätswarnungen", expanded=True):
            for w in warnings:
                st.warning(w)

    modes = fixture.get("modes") or []
    if modes:
        st.subheader("2) Kanalmap prüfen/korrigieren")
        mode_names = [m.get("name") or f"Mode {i+1}" for i, m in enumerate(modes)]
        selected_name = st.selectbox("DMX-Modus", mode_names)
        idx = mode_names.index(selected_name)
        mode = modes[idx]
        st.write(f"Erkannte Kanalanzahl: **{mode.get('channel_count')}**")

        df = mode_to_df(mode)
        edited = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "attribute": st.column_config.SelectboxColumn(
                    "attribute",
                    options=[
                        "Dimmer", "Shutter", "Strobe", "Pan", "Tilt", "PanTiltSpeed",
                        "ColorAdd_R", "ColorAdd_G", "ColorAdd_B", "ColorAdd_W", "ColorMacro",
                        "Macro", "MacroSpeed", "Reset", "NoFunction", "Gobo", "GoboRotate",
                        "Prism", "PrismRotate", "Zoom", "Focus", "Frost", "Iris", "Unknown"
                    ],
                )
            }
        )

        if st.button("Änderungen für diesen Modus übernehmen"):
            fixture["modes"][idx] = df_to_mode(mode, edited)
            st.session_state["fixture_json"] = fixture
            st.success("Änderungen übernommen")

        st.subheader("3) Export")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📦 GDTF bauen", type="primary"):
                # Aktuelle Tabelle automatisch in den Modus zurückschreiben
                fixture["modes"][idx] = df_to_mode(mode, edited)
                gdtf_bytes, gdtf_name, description_xml = build_gdtf_package(fixture)
                csv_bytes = build_channel_csv(fixture)
                st.session_state["gdtf_bytes"] = gdtf_bytes
                st.session_state["gdtf_name"] = gdtf_name
                st.session_state["description_xml"] = description_xml
                st.session_state["csv_bytes"] = csv_bytes
                st.success("GDTF erzeugt")
        with col2:
            st.download_button(
                "Download fixture.json",
                data=json.dumps(fixture, ensure_ascii=False, indent=2).encode("utf-8"),
                file_name="fixture.json",
                mime="application/json",
            )
        with col3:
            st.download_button(
                "Download Kanalmap CSV",
                data=build_channel_csv(fixture),
                file_name="channel_map.csv",
                mime="text/csv",
            )

        if st.session_state.get("gdtf_bytes"):
            st.download_button(
                "⬇️ Download .gdtf",
                data=st.session_state["gdtf_bytes"],
                file_name=st.session_state["gdtf_name"],
                mime="application/zip",
                type="primary",
            )
            with st.expander("description.xml anzeigen"):
                st.code(st.session_state["description_xml"].decode("utf-8"), language="xml")

    with st.expander("Rohdaten JSON"):
        st.json(fixture)
else:
    st.markdown("""
### So benutzt du die App
1. Manual oder DMX-Sheet als PDF/JPG/PNG hochladen.  
2. Hersteller/Modell optional eintragen.  
3. **KI analysieren** klicken.  
4. Kanalmap prüfen und korrigieren.  
5. **GDTF bauen** klicken und Datei herunterladen.  

Hinweis: Das ist ein MVP. Die erzeugte GDTF sollte danach im GDTF Builder oder grandMA3 getestet werden.
""")
