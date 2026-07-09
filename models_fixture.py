from __future__ import annotations
import json
from typing import Any, Dict


def fixture_to_json_bytes(fixture: Dict[str, Any]) -> bytes:
    return json.dumps(fixture, ensure_ascii=False, indent=2).encode("utf-8")


def normalize_fixture(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        return {"manufacturer": None, "fixture_name": None, "notes": "", "physical": {}, "modes": [], "warnings": ["AI did not return an object."]}
    data.setdefault("manufacturer", None)
    data.setdefault("fixture_name", None)
    data.setdefault("notes", "")
    data.setdefault("physical", {})
    data.setdefault("modes", [])
    data.setdefault("warnings", [])
    for mode in data["modes"]:
        mode.setdefault("name", "Unknown")
        mode.setdefault("channel_count", 0)
        mode.setdefault("confidence", 0)
        mode.setdefault("channels", [])
        for ch in mode["channels"]:
            ch.setdefault("ranges", [])
    return data
