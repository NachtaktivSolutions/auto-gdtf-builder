from __future__ import annotations

import json
from typing import Any, Dict, List


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
                "channel_count": int(mode.get("channel_count") or 0),
                "confidence": float(mode.get("confidence") or 0),
                "channels": [],
            }
            for ch in mode.get("channels", []) or []:
                if not isinstance(ch, dict):
                    continue
                try:
                    channel_no = int(ch.get("channel"))
                except Exception:
                    continue
                ranges = []
                for r in ch.get("ranges", []) or []:
                    if not isinstance(r, dict):
                        continue
                    try:
                        ranges.append({
                            "from": int(r.get("from", 0)),
                            "to": int(r.get("to", 255)),
                            "name": str(r.get("name") or ""),
                            "description": str(r.get("description") or ""),
                        })
                    except Exception:
                        pass
                m["channels"].append({
                    "channel": channel_no,
                    "fine_channel": _to_int_or_none(ch.get("fine_channel")),
                    "attribute": str(ch.get("attribute") or "Unknown"),
                    "raw_label": str(ch.get("raw_label") or ""),
                    "raw_description": str(ch.get("raw_description") or ""),
                    "geometry": ch.get("geometry"),
                    "default_value": _to_int_or_none(ch.get("default_value")),
                    "highlight_value": _to_int_or_none(ch.get("highlight_value")),
                    "ranges": ranges,
                })
            m["channels"].sort(key=lambda x: x["channel"])
            fixture["modes"].append(m)

    if isinstance(data.get("warnings"), list):
        fixture["warnings"].extend([str(w) for w in data["warnings"]])

    return fixture


def _to_int_or_none(v):
    if v is None or v == "":
        return None
    try:
        return int(v)
    except Exception:
        return None


def fixture_to_json_bytes(fixture: Dict[str, Any]) -> bytes:
    return json.dumps(fixture, ensure_ascii=False, indent=2).encode("utf-8")
