import csv
import io
import re
import uuid
import zipfile
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Tuple


def _safe_name(value: str, default: str = "Fixture") -> str:
    value = (value or default).strip()
    value = re.sub(r"[^A-Za-z0-9_@.\- ]+", "_", value)
    value = re.sub(r"\s+", "_", value)
    return value or default


def _gdtf_attribute(attr: str) -> str:
    mapping = {
        "Dimmer": "Dimmer",
        "Shutter": "Shutter1",
        "Strobe": "Shutter1",
        "Pan": "Pan",
        "Tilt": "Tilt",
        "PanTiltSpeed": "PanTiltSpeed",
        "ColorAdd_R": "ColorAdd_R",
        "ColorAdd_G": "ColorAdd_G",
        "ColorAdd_B": "ColorAdd_B",
        "ColorAdd_W": "ColorAdd_W",
        "ColorMacro": "ColorMacro1",
        "Macro": "Macro1",
        "MacroSpeed": "Macro1Speed",
        "Reset": "FixtureGlobalReset",
        "Gobo": "Gobo1",
        "GoboRotate": "Gobo1PosRotate",
        "Prism": "Prism1",
        "PrismRotate": "Prism1PosRotate",
        "Zoom": "Zoom",
        "Focus": "Focus1",
        "Frost": "Frost1",
        "Iris": "Iris1",
        "NoFunction": "NoFeature",
        "Unknown": "NoFeature",
    }
    return mapping.get(attr or "Unknown", "NoFeature")


def _feature_group_for_attribute(attr: str) -> Tuple[str, str]:
    attr = attr or "Unknown"
    if attr in {"Pan", "Tilt", "PanTiltSpeed"}:
        return "Position", "POSITION"
    if attr.startswith("Color") or attr in {"ColorMacro"}:
        return "Color", "COLOR"
    if attr in {"Dimmer"}:
        return "Dimmer", "DIMMER"
    if attr in {"Shutter", "Strobe", "Zoom", "Focus", "Frost", "Iris"}:
        return "Beam", "BEAM"
    if attr in {"Gobo", "GoboRotate"}:
        return "Gobo", "GOBO"
    if attr in {"Macro", "MacroSpeed", "Reset", "NoFunction", "Unknown"}:
        return "Control", "CONTROL"
    return "Control", "CONTROL"


def _mode_channels(mode: Dict[str, Any]) -> List[Dict[str, Any]]:
    channels = mode.get("channels") or []
    return sorted(channels, key=lambda c: int(c.get("channel") or 9999))


def _build_description_xml(fixture: Dict[str, Any]) -> bytes:
    manufacturer = fixture.get("manufacturer") or "Unknown"
    fixture_name = fixture.get("fixture_name") or "Generated Fixture"
    short_name = fixture.get("short_name") or fixture_name[:16]
    physical = fixture.get("physical") or {}
    beam_angle = str(physical.get("beam_angle_degrees") or 10)

    root = ET.Element("GDTF", {"DataVersion": "1.2"})
    ft = ET.SubElement(root, "FixtureType", {
        "Name": fixture_name,
        "ShortName": short_name,
        "LongName": fixture_name,
        "Manufacturer": manufacturer,
        "FixtureTypeID": str(uuid.uuid4()),
        "Thumbnail": "thumbnail",
    })

    # AttributeDefinitions: bewusst schlank gehalten. Viele Konsolen akzeptieren die Standard-Attribute.
    ad = ET.SubElement(ft, "AttributeDefinitions")
    feature_groups = ET.SubElement(ad, "FeatureGroups")
    for fg_name in ["Dimmer", "Position", "Color", "Beam", "Gobo", "Control"]:
        ET.SubElement(feature_groups, "FeatureGroup", {"Name": fg_name, "Pretty": fg_name})

    activation_groups = ET.SubElement(ad, "ActivationGroups")
    ET.SubElement(activation_groups, "ActivationGroup", {"Name": "PanTilt"})
    ET.SubElement(activation_groups, "ActivationGroup", {"Name": "Color"})

    # Geometrie-Struktur aus allen verwendeten geometry-Namen ableiten.
    geometries = ET.SubElement(ft, "Geometries")
    base = ET.SubElement(geometries, "Geometry", {"Name": "Base"})
    geom_names = set()
    for mode in fixture.get("modes", []):
        for ch in mode.get("channels", []):
            geom_names.add(ch.get("geometry") or "Base")
    geom_names.discard("Base")
    if not geom_names:
        geom_names.add("Head 1")
    for geom in sorted(geom_names):
        axis_pan = ET.SubElement(base, "GeometryAxis", {"Name": f"{_safe_name(geom)}_Pan"})
        axis_tilt = ET.SubElement(axis_pan, "GeometryAxis", {"Name": f"{_safe_name(geom)}_Tilt"})
        ET.SubElement(axis_tilt, "GeometryBeam", {
            "Name": _safe_name(geom),
            "LampType": physical.get("lamp_type") or "LED",
            "BeamType": "Beam",
            "BeamAngle": beam_angle,
            "FieldAngle": str(max(float(beam_angle), 1.0) + 1.0),
            "ColorRenderingIndex": "80",
            "LuminousFlux": "1000",
        })

    dmx_modes = ET.SubElement(ft, "DMXModes")
    for mode in fixture.get("modes", []):
        mode_name = mode.get("name") or f"{mode.get('channel_count', 'Unknown')}CH"
        dmx_mode = ET.SubElement(dmx_modes, "DMXMode", {"Name": mode_name, "Geometry": "Base"})
        dmx_channels = ET.SubElement(dmx_mode, "DMXChannels")

        for ch in _mode_channels(mode):
            try:
                channel_num = int(ch.get("channel"))
            except Exception:
                continue
            fine = ch.get("fine_channel")
            offsets = str(channel_num)
            if fine not in (None, "", 0, "0"):
                try:
                    offsets = f"{channel_num},{int(fine)}"
                except Exception:
                    pass

            default = ch.get("default")
            dmx_attrs = {"DMXBreak": "1", "Offset": offsets, "Geometry": _safe_name(ch.get("geometry") or "Base")}
            if default is not None:
                try:
                    dmx_attrs["Default"] = str(int(default))
                except Exception:
                    pass
            dmx_channel = ET.SubElement(dmx_channels, "DMXChannel", dmx_attrs)

            g_attr = _gdtf_attribute(ch.get("attribute"))
            logical = ET.SubElement(dmx_channel, "LogicalChannel", {"Attribute": g_attr})
            ranges = ch.get("ranges") or [{"from": 0, "to": 255, "name": ch.get("function") or g_attr}]
            # ChannelFunction umfasst erstmal den ganzen 8-bit Bereich. Ranges werden als ChannelSets abgebildet.
            cf = ET.SubElement(logical, "ChannelFunction", {
                "Name": ch.get("function") or g_attr,
                "Attribute": g_attr,
                "OriginalAttribute": ch.get("attribute") or "Unknown",
                "DMXFrom": "0/1",
                "DMXTo": "255/1",
                "PhysicalFrom": "0",
                "PhysicalTo": "1",
            })
            for r in ranges:
                try:
                    fr = int(r.get("from", 0))
                    to = int(r.get("to", 255))
                except Exception:
                    fr, to = 0, 255
                ET.SubElement(cf, "ChannelSet", {
                    "Name": str(r.get("name") or ch.get("function") or g_attr),
                    "DMXFrom": f"{fr}/1",
                    "DMXTo": f"{to}/1",
                })

    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _thumbnail_svg() -> bytes:
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
<rect width="256" height="256" rx="24" fill="#111111"/>
<text x="128" y="112" text-anchor="middle" font-size="34" font-family="Arial" fill="#ffd400">GDTF</text>
<text x="128" y="154" text-anchor="middle" font-size="18" font-family="Arial" fill="#ffffff">AI Generated</text>
</svg>'''
    return svg.encode("utf-8")


def build_gdtf_package(fixture: Dict[str, Any]) -> Tuple[bytes, str, bytes]:
    """Erzeugt .gdtf Bytes, Dateiname und description.xml Bytes."""
    description = _build_description_xml(fixture)
    filename = f"{_safe_name(fixture.get('manufacturer'), 'Unknown')}@{_safe_name(fixture.get('fixture_name'), 'Fixture')}@AI_Generated.gdtf"
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("description.xml", description)
        zf.writestr("thumbnail.svg", _thumbnail_svg())
    return bio.getvalue(), filename, description


def build_channel_csv(fixture: Dict[str, Any]) -> bytes:
    out = io.StringIO()
    writer = csv.writer(out, delimiter=";")
    writer.writerow(["mode", "channel", "fine_channel", "geometry", "attribute", "function", "ranges"])
    for mode in fixture.get("modes", []):
        for ch in _mode_channels(mode):
            ranges = " | ".join([f"{r.get('from')}-{r.get('to')}: {r.get('name')}" for r in (ch.get("ranges") or [])])
            writer.writerow([
                mode.get("name"), ch.get("channel"), ch.get("fine_channel"), ch.get("geometry"),
                ch.get("attribute"), ch.get("function"), ranges
            ])
    return out.getvalue().encode("utf-8-sig")


def validate_fixture_json(fixture: Dict[str, Any]) -> List[str]:
    warnings: List[str] = []
    if not fixture.get("modes"):
        warnings.append("Keine DMX-Modi erkannt.")
        return warnings
    for mode in fixture.get("modes", []):
        name = mode.get("name") or "Unnamed"
        count = int(mode.get("channel_count") or 0)
        used = []
        for ch in mode.get("channels", []):
            c = ch.get("channel")
            if c:
                used.append(int(c))
            f = ch.get("fine_channel")
            if f:
                used.append(int(f))
            for r in ch.get("ranges", []) or []:
                if int(r.get("from", 0)) < 0 or int(r.get("to", 255)) > 255:
                    warnings.append(f"{name}: Range ausserhalb 0-255 bei Kanal {c}.")
        if count and used and max(used) > count:
            warnings.append(f"{name}: Hoechster verwendeter Kanal {max(used)} groesser als channel_count {count}.")
        duplicates = sorted({x for x in used if used.count(x) > 1})
        if duplicates:
            warnings.append(f"{name}: Doppelt verwendete Kanaele: {duplicates}")
        if count and max(used or [0]) < count:
            warnings.append(f"{name}: channel_count ist {count}, aber hoechster erkannter Kanal ist {max(used or [0])}. Das kann okay sein, sollte aber geprueft werden.")
    return warnings
