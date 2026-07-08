from __future__ import annotations
import json, zipfile, xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def parse_gdtf_reference(gdtf_path: str, max_channels: int = 80) -> dict[str, Any]:
    """Extract a compact learning reference from a working .gdtf.

    This does not fully validate GDTF. It extracts fixture metadata, DMX modes,
    offsets, channel function names, and attributes as context for the next AI run.
    """
    p = Path(gdtf_path)
    with zipfile.ZipFile(p, "r") as z:
        xml_bytes = z.read("description.xml")
    root = ET.fromstring(xml_bytes)
    ft = root.find("FixtureType") or root.find(".//FixtureType")
    result: dict[str, Any] = {"source": p.name, "fixture_type": {}, "modes": []}
    if ft is not None:
        result["fixture_type"] = dict(ft.attrib)
        for dm in ft.findall(".//DMXMode"):
            mode_info: dict[str, Any] = {"name": dm.attrib.get("Name", "Mode"), "channels": []}
            for dch in dm.findall(".//DMXChannel")[:max_channels]:
                ch_info: dict[str, Any] = {
                    "offset": dch.attrib.get("Offset", ""),
                    "geometry": dch.attrib.get("Geometry", ""),
                    "default": dch.attrib.get("Default", ""),
                    "functions": [],
                }
                for cf in dch.findall(".//ChannelFunction")[:8]:
                    ch_info["functions"].append({
                        "name": cf.attrib.get("Name", ""),
                        "attribute": cf.attrib.get("Attribute", ""),
                        "dmx_from": cf.attrib.get("DMXFrom", ""),
                    })
                mode_info["channels"].append(ch_info)
            result["modes"].append(mode_info)
    return result


def reference_to_prompt_context(ref: dict[str, Any]) -> str:
    return "GDTF-REFERENZBEISPIEL:\n" + json.dumps(ref, ensure_ascii=False, indent=2)[:12000]
