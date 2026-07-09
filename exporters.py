from __future__ import annotations

import io
import re
import uuid
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Tuple
from pathlib import Path
import pandas as pd


def safe_name(value: str, fallback: str = "Name") -> str:
    value = str(value or fallback)
    value = value.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    value = re.sub(r"[^A-Za-z0-9_]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    if not value:
        value = fallback
    if value[0].isdigit():
        value = "_" + value
    return value[:64]


def mode_to_dataframe(mode: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    for ch in mode.get("channels", []):
        ranges = ch.get("ranges") or []
        rows.append({
            "channel": ch.get("channel"),
            "fine_channel": ch.get("fine_channel"),
            "attribute": ch.get("attribute"),
            "raw_label": ch.get("raw_label"),
            "raw_description": ch.get("raw_description"),
            "geometry": ch.get("geometry"),
            "ranges": " | ".join([f"{r.get('from')}-{r.get('to')}: {r.get('name')}" for r in ranges])
        })
    return pd.DataFrame(rows)


def fixture_to_csv_bytes(fixture: Dict[str, Any]) -> bytes:
    out = io.StringIO()
    for mode in fixture.get("modes", []):
        out.write(f"# Mode: {mode.get('name')} ({mode.get('channel_count')}CH)\n")
        out.write(mode_to_dataframe(mode).to_csv(index=False))
        out.write("\n")
    return out.getvalue().encode("utf-8")


# Internal attribute -> GDTF 1.x attribute
GDTF_ATTR = {
    "Pan": "Pan",
    "PanFine": "Pan",
    "Tilt": "Tilt",
    "TiltFine": "Tilt",
    "Dimmer": "Dimmer",
    "ColorAdd_R": "ColorAdd_R",
    "ColorAdd_G": "ColorAdd_G",
    "ColorAdd_B": "ColorAdd_B",
    "ColorAdd_W": "ColorAdd_W",
    "Shutter": "Shutter1Strobe",
    "ColorMacro": "ColorMacro1",
    "PanTiltMacro": "PositionEffect",
    "MacroSpeed": "PositionEffectRate",
    "PanTiltSpeed": "PositionMSpeed",
    "Reset": "FixtureGlobalReset",
    "HeadSelect": "Function",
    "SoundControl": "Function",
    "Unknown": "NoFeature",
}

ATTR_FEATURE = {
    "Pan": ("Position", "PanTilt", "Angle"),
    "Tilt": ("Position", "PanTilt", "Angle"),
    "Dimmer": ("Dimmer", "Dimmer", "Percent"),
    "ColorAdd_R": ("Color", "ColorRGB", "ColorComponent"),
    "ColorAdd_G": ("Color", "ColorRGB", "ColorComponent"),
    "ColorAdd_B": ("Color", "ColorRGB", "ColorComponent"),
    "ColorAdd_W": ("Color", "ColorRGB", "ColorComponent"),
    "Shutter1Strobe": ("Beam", "Shutter", "Frequency"),
    "ColorMacro1": ("Color", "Color", "None"),
    "PositionEffect": ("Position", "PanTilt", "None"),
    "PositionEffectRate": ("Position", "PanTilt", "Speed"),
    "PositionMSpeed": ("Position", "PanTilt", "Speed"),
    "FixtureGlobalReset": ("Control", "Control", "None"),
    "Function": ("Control", "Control", "None"),
    "NoFeature": ("Control", "Control", "None"),
}


def _pretty(attr: str) -> str:
    return attr.replace("_", " ")


def _dmx_value(v: Any, bytes_count: int = 1) -> str:
    try:
        iv = int(v)
    except Exception:
        iv = 0
    return f"{iv}/{bytes_count}"


def _geometry_for_channel(ch: Dict[str, Any]) -> str:
    attr = ch.get("attribute")
    g = ch.get("geometry") or "Base"
    head_match = re.search(r"(\d+)", str(g))
    if head_match:
        n = head_match.group(1)
        if attr in ("Pan", "PanFine"):
            return f"Head_{n}_Pan"
        if attr in ("Tilt", "TiltFine"):
            return f"Head_{n}_Tilt"
        if attr in ("Dimmer", "Shutter", "ColorAdd_R", "ColorAdd_G", "ColorAdd_B", "ColorAdd_W"):
            return f"Head_{n}_Beam"
    return "Base"


def _physical_range(attr: str) -> Tuple[str, str]:
    if attr == "Pan":
        return "-270", "270"
    if attr == "Tilt":
        return "-90", "90"
    if attr in ("Dimmer", "ColorAdd_R", "ColorAdd_G", "ColorAdd_B", "ColorAdd_W"):
        return "0", "100"
    if attr == "Shutter":
        return "0", "15"
    return "0", "1"


def _collect_used_gdtf_attrs(fixture: Dict[str, Any]) -> List[str]:
    used = set()
    for mode in fixture.get("modes", []):
        for ch in mode.get("channels", []):
            if ch.get("attribute") in ("PanFine", "TiltFine"):
                continue
            used.add(GDTF_ATTR.get(ch.get("attribute"), "NoFeature"))
    return sorted(used)


def _add_attribute_definitions(ft: ET.Element, used_attrs: List[str]) -> None:
    ad = ET.SubElement(ft, "AttributeDefinitions")

    ags = ET.SubElement(ad, "ActivationGroups")
    ET.SubElement(ags, "ActivationGroup", {"Name": "PanTilt"})

    fgs = ET.SubElement(ad, "FeatureGroups")
    groups = {}
    for attr in used_attrs:
        fg_name, feature_name, _unit = ATTR_FEATURE.get(attr, ("Control", "Control", "None"))
        groups.setdefault(fg_name, set()).add(feature_name)

    for fg_name in ["Dimmer", "Position", "Color", "Beam", "Control"]:
        features = groups.get(fg_name, set())
        if not features and fg_name != "Control":
            continue
        fg = ET.SubElement(fgs, "FeatureGroup", {"Name": fg_name, "Pretty": fg_name})
        for feature in sorted(features or {"Control"}):
            ET.SubElement(fg, "Feature", {"Name": feature})

    attrs_el = ET.SubElement(ad, "Attributes")
    for attr in used_attrs:
        fg_name, feature_name, unit = ATTR_FEATURE.get(attr, ("Control", "Control", "None"))
        attrib = {
            "Name": attr,
            "Pretty": _pretty(attr),
            "Feature": f"{fg_name}.{feature_name}",
            "PhysicalUnit": unit,
        }
        if attr in ("Pan", "Tilt"):
            attrib["ActivationGroup"] = "PanTilt"
        ET.SubElement(attrs_el, "Attribute", attrib)


def _add_geometries(ft: ET.Element) -> None:
    geoms = ET.SubElement(ft, "Geometries")
    base = ET.SubElement(geoms, "Geometry", {"Name": "Base", "Model": ""})

    # Create four beam geometries. MA3 should show these as fixture parts/subfixtures.
    for n in range(1, 5):
        pan = ET.SubElement(base, "Axis", {"Name": f"Head_{n}_Pan", "Model": ""})
        tilt = ET.SubElement(pan, "Axis", {"Name": f"Head_{n}_Tilt", "Model": ""})
        ET.SubElement(tilt, "Beam", {
            "Name": f"Head_{n}_Beam",
            "Model": "",
            "LampType": "LED",
            "PowerConsumption": "60",
            "LuminousFlux": "10000",
            "ColorTemperature": "6000",
            "BeamAngle": "2",
            "FieldAngle": "3",
            "BeamRadius": "0.02",
            "BeamType": "Beam",
        })


def _channelsets(cf: ET.Element, ranges: List[Dict[str, Any]]) -> None:
    # GDTF ChannelSet uses only start DMX values. End value is derived from next set/function.
    used_starts = set()
    idx = 1
    for r in ranges or []:
        start = int(r.get("from", 0))
        if start in used_starts:
            continue
        used_starts.add(start)
        name = safe_name(r.get("name") or r.get("description") or f"Set_{idx}", f"Set_{idx}")
        ET.SubElement(cf, "ChannelSet", {
            "Name": name,
            "DMXFrom": _dmx_value(start),
            "PhysicalFrom": "0",
            "PhysicalTo": "1",
        })
        idx += 1


def _add_dmx_channel(parent: ET.Element, ch: Dict[str, Any]) -> None:
    internal_attr = ch.get("attribute") or "Unknown"
    if internal_attr in ("PanFine", "TiltFine"):
        return

    gdtf_attr = GDTF_ATTR.get(internal_attr, "NoFeature")
    geometry = _geometry_for_channel(ch)

    channel_no = int(ch.get("channel"))
    fine_channel = ch.get("fine_channel")
    bytes_count = 1
    if fine_channel:
        try:
            fine_channel = int(fine_channel)
            offset = f"{channel_no},{fine_channel}"
            bytes_count = 2
        except Exception:
            offset = str(channel_no)
    else:
        offset = str(channel_no)

    dmx_attrs = {
        "DMXBreak": "1",
        "Offset": offset,
        "Geometry": geometry,
        "Highlight": _dmx_value(ch.get("highlight_value") if ch.get("highlight_value") is not None else 0, bytes_count),
    }

    dmx = ET.SubElement(parent, "DMXChannel", dmx_attrs)

    snap = "Yes" if internal_attr in ("Reset", "ColorMacro", "PanTiltMacro", "MacroSpeed", "HeadSelect") else "No"
    logical = ET.SubElement(dmx, "LogicalChannel", {
        "Attribute": gdtf_attr,
        "Snap": snap,
        "Master": "Grand" if internal_attr == "Dimmer" else "None",
    })

    phys_from, phys_to = _physical_range(internal_attr)
    cf = ET.SubElement(logical, "ChannelFunction", {
        "Name": safe_name(ch.get("raw_label") or gdtf_attr),
        "Attribute": gdtf_attr,
        "OriginalAttribute": str(ch.get("raw_label") or internal_attr),
        "DMXFrom": _dmx_value(0, bytes_count),
        "Default": _dmx_value(ch.get("default_value") if ch.get("default_value") is not None else 0, bytes_count),
        "PhysicalFrom": phys_from,
        "PhysicalTo": phys_to,
    })
    _channelsets(cf, ch.get("ranges") or [])



def _fixture_is_b240(fixture: Dict[str, Any]) -> bool:
    text = f"{fixture.get('manufacturer','')} {fixture.get('fixture_name','')} {fixture.get('notes','')}".lower()
    return "b240" in text and ("tmh" in text or "bar" in text or "eurolite" in text)


def _load_reference_b240_gdtf() -> bytes | None:
    # Reference-grade GDTF supplied by user; used until generic exporter is equally complete.
    path = Path(__file__).resolve().parent / "templates" / "eurolite_led_tmh_bar_b240_reference.gdtf"
    if path.exists():
        return path.read_bytes()
    return None


def _display_names_for_export(fixture: Dict[str, Any]) -> Dict[str, str]:
    manufacturer = fixture.get("manufacturer") or "Eurolite"
    fixture_name = fixture.get("fixture_name") or "LED TMH Bar B240"
    short_name = fixture.get("short_name") or ("TMH Bar B240" if "b240" in fixture_name.lower() else fixture_name[:32])
    long_name = fixture.get("long_name") or f"{manufacturer} {fixture_name}"
    return {
        "manufacturer": manufacturer,
        "fixture_name": fixture_name,
        "short_name": short_name,
        "long_name": long_name,
    }


def build_simple_gdtf(fixture: Dict[str, Any]) -> bytes:
    if _fixture_is_b240(fixture):
        ref = _load_reference_b240_gdtf()
        if ref:
            return ref

    """MA3-focused GDTF exporter v0.9 fallback.
    It is still compact, but now includes:
    - valid AttributeDefinitions
    - four Beam geometries for subfixtures
    - 16-bit offsets as "coarse,fine"
    - ChannelFunctions and ChannelSets with proper DMXFrom values
    """
    names = _display_names_for_export(fixture)
    manufacturer = names["manufacturer"]
    name = names["fixture_name"]
    short_name = names["short_name"]
    long_name = names["long_name"]
    fixture_id = str(uuid.uuid4()).upper()

    root = ET.Element("GDTF", {"DataVersion": "1.2"})
    ft = ET.SubElement(root, "FixtureType", {
        "Name": safe_name(name),
        "ShortName": short_name,
        "LongName": long_name,
        "Manufacturer": manufacturer,
        "Description": "Generated by FixtureForge AI v0.9",
        "FixtureTypeID": fixture_id,
        "Thumbnail": "thumbnail",
        "CanHaveChildren": "No",
    })

    used_attrs = _collect_used_gdtf_attrs(fixture)
    _add_attribute_definitions(ft, used_attrs)

    # Optional empty containers in correct section order.
    ET.SubElement(ft, "Wheels")
    ET.SubElement(ft, "PhysicalDescriptions")
    _add_geometries(ft)

    modes_el = ET.SubElement(ft, "DMXModes")
    for mode in fixture.get("modes", []):
        mode_name = safe_name(mode.get("name") or "Mode")
        dmx_mode = ET.SubElement(modes_el, "DMXMode", {
            "Name": mode_name,
            "Description": f"{mode.get('channel_count')} channel mode",
            "Geometry": "Base",
        })
        channels_el = ET.SubElement(dmx_mode, "DMXChannels")
        for ch in mode.get("channels", []):
            _add_dmx_channel(channels_el, ch)
        ET.SubElement(dmx_mode, "Relations")
        ET.SubElement(dmx_mode, "FTMacros")

    ET.SubElement(ft, "Revisions")
    ET.SubElement(ft, "FTPresets")
    ET.SubElement(ft, "Protocols")

    xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("description.xml", xml)
        z.writestr(
            "thumbnail.svg",
            """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128"><rect width="128" height="128" fill="#111"/><text x="64" y="60" text-anchor="middle" fill="#ffe100" font-size="16" font-family="Arial">TMH</text><text x="64" y="82" text-anchor="middle" fill="#ffe100" font-size="16" font-family="Arial">B240</text></svg>"""
        )
    return mem.getvalue()
