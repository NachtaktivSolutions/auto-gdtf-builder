from __future__ import annotations

import json
from typing import Any, Dict


def empty_fixture() -> Dict[str, Any]:
    return {
        "manufacturer": None,
        "fixture_name": None,
        "notes": "",
        "physical": {
            "pan_degrees": None,
            "tilt_degrees": None,
            "beam_angle_degrees": None,
            "weight_kg": None,
            "width_mm": None,
            "height_mm": None,
            "depth_mm": None,
        },
        "modes": [],
        "warnings": [],
    }


def normalize_fixture(data: Dict[str, Any]) -> Dict[str, Any]:
    fixture = empty_fixture()
    if not isinstance(data, dict):
        fixture["warnings"].append("AI result was not a JSON object.")
        return fixture

    for key in ["manufacturer", "fixture_name", "notes"]:
        if key in data:
            fixture[key] = data.get(key)

    if isinstance(data.get("physical"), dict):
        fixture["physical"].update(data["physical"])

    modes = data.get("modes", [])
    if isinstance(modes, list):
        for mode in modes:
            if not isinstance(mode, dict):
                continue
            m = {
                "name": str(mode.get("name") or "Unknown"),
                "channel_count": _to_int(mode.get("channel_count"), 0),
                "confidence": _to_float(mode.get("confidence"), 0),
                "channels": [],
            }
            for ch in mode.get("channels", []) or []:
                if not isinstance(ch, dict):
                    continue
                channel_no = _to_int(ch.get("channel"), None)
                if channel_no is None:
                    continue
                ranges = []
                for r in ch.get("ranges", []) or []:
                    if not isinstance(r, dict):
                        continue
                    ranges.append({
                        "from": _to_int(r.get("from"), 0),
                        "to": _to_int(r.get("to"), 255),
                        "name": str(r.get("name") or ""),
                        "description": str(r.get("description") or ""),
                    })
                m["channels"].append({
                    "channel": channel_no,
                    "fine_channel": _to_int(ch.get("fine_channel"), None),
                    "attribute": str(ch.get("attribute") or "Unknown"),
                    "raw_label": str(ch.get("raw_label") or ""),
                    "raw_description": str(ch.get("raw_description") or ""),
                    "geometry": ch.get("geometry"),
                    "default_value": _to_int(ch.get("default_value"), None),
                    "highlight_value": _to_int(ch.get("highlight_value"), None),
                    "ranges": ranges,
                })
            m["channels"].sort(key=lambda x: x["channel"])
            fixture["modes"].append(m)

    if isinstance(data.get("warnings"), list):
        fixture["warnings"].extend([str(w) for w in data["warnings"]])

    return fixture


def _to_int(v, default):
    if v is None or v == "":
        return default
    try:
        return int(float(v))
    except Exception:
        return default


def _to_float(v, default):
    if v is None or v == "":
        return default
    try:
        return float(v)
    except Exception:
        return default


def fixture_to_json_bytes(fixture: Dict[str, Any]) -> bytes:
    return json.dumps(fixture, ensure_ascii=False, indent=2).encode("utf-8")
