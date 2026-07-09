from __future__ import annotations

import re
from typing import Dict, Any


def clean_filename(value: str, fallback: str = "fixture") -> str:
    value = str(value or fallback)
    value = value.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or fallback


def default_display_names(fixture: Dict[str, Any]) -> Dict[str, str]:
    manufacturer = fixture.get("manufacturer") or "Eurolite"
    fixture_name = fixture.get("fixture_name") or "LED TMH Bar B240"

    # Friendly defaults for B240
    if "b240" in fixture_name.lower():
        return {
            "manufacturer": "Eurolite",
            "fixture_name": "LED TMH Bar B240",
            "short_name": "TMH Bar B240",
            "long_name": "Eurolite LED TMH Bar B240",
            "file_prefix": "Eurolite_LED_TMH_Bar_B240",
        }

    short_name = fixture_name
    if len(short_name) > 28:
        short_name = short_name[:28].rstrip()
    return {
        "manufacturer": manufacturer,
        "fixture_name": fixture_name,
        "short_name": short_name,
        "long_name": f"{manufacturer} {fixture_name}",
        "file_prefix": clean_filename(f"{manufacturer}_{fixture_name}"),
    }


def apply_fixture_names(fixture: Dict[str, Any], names: Dict[str, str]) -> Dict[str, Any]:
    fixture["manufacturer"] = names.get("manufacturer") or fixture.get("manufacturer")
    fixture["fixture_name"] = names.get("fixture_name") or fixture.get("fixture_name")
    fixture["short_name"] = names.get("short_name") or fixture.get("short_name")
    fixture["long_name"] = names.get("long_name") or fixture.get("long_name")
    fixture["file_prefix"] = names.get("file_prefix") or fixture.get("file_prefix")
    return fixture


def pretty_channel_label(channel: Dict[str, Any]) -> str:
    attr = channel.get("attribute") or "Unknown"
    geom = channel.get("geometry") or ""
    head = None
    m = re.search(r"(\d+)", str(geom))
    if m:
        head = m.group(1)

    attr_names = {
        "Pan": "Pan",
        "PanFine": "Pan Fine",
        "Tilt": "Tilt",
        "TiltFine": "Tilt Fine",
        "PanTiltSpeed": "P/T Speed",
        "Shutter": "Shutter",
        "Dimmer": "Dimmer",
        "ColorAdd_R": "Red",
        "ColorAdd_G": "Green",
        "ColorAdd_B": "Blue",
        "ColorAdd_W": "White",
        "PanTiltMacro": "Movement Macro",
        "ColorMacro": "Color Macro",
        "MacroSpeed": "Macro Speed",
        "Reset": "Reset",
        "HeadSelect": "Head Select",
    }
    name = attr_names.get(attr, attr)
    if head and attr in {"Pan", "PanFine", "Tilt", "TiltFine", "PanTiltSpeed", "Shutter", "Dimmer", "ColorAdd_R", "ColorAdd_G", "ColorAdd_B", "ColorAdd_W"}:
        return f"Head {head} {name}"
    return name


def polish_fixture_labels(fixture: Dict[str, Any]) -> Dict[str, Any]:
    for mode in fixture.get("modes", []):
        # Normalize mode names
        cc = mode.get("channel_count")
        if cc:
            mode["name"] = f"{cc}CH"
        for ch in mode.get("channels", []):
            ch["raw_label"] = pretty_channel_label(ch)
            if not ch.get("raw_description") or ch.get("raw_description") == ch.get("raw_label"):
                ch["raw_description"] = ch["raw_label"]
            # Friendly geometry names
            geom = ch.get("geometry")
            if geom:
                m = re.search(r"(\d+)", str(geom))
                if m:
                    ch["geometry"] = f"Head {m.group(1)}"
    return fixture
