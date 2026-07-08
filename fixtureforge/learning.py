from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from .schema import Fixture

DATA_DIR = Path("training_data")
DATA_DIR.mkdir(exist_ok=True)

def make_training_record(original: dict, corrected: Fixture, note: str = "") -> dict[str, Any]:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return {
        "created_utc": ts,
        "note": note,
        "manufacturer": corrected.manufacturer,
        "fixture_name": corrected.fixture_name,
        "original_ai_result": original,
        "corrected_fixture": corrected.model_dump(),
    }

def save_training_example(original: dict, corrected: Fixture, note: str = "") -> Path:
    record = make_training_record(original, corrected, note)
    path = DATA_DIR / f"training_{record['created_utc']}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

def records_to_jsonl(records: list[dict[str, Any]]) -> str:
    return "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + ("\n" if records else "")

def parse_jsonl(text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out

def build_knowledge_context(records: list[dict[str, Any]], manual_rules: str = "", max_records: int = 5) -> str:
    """Condense confirmed corrections into prompt context. This is prompt-training, not fine-tuning."""
    parts: list[str] = []
    if manual_rules.strip():
        parts.append("MANUELLE REGELN:\n" + manual_rules.strip())

    if records:
        parts.append("BESTÄTIGTE KORREKTURBEISPIELE:")
        for i, rec in enumerate(records[-max_records:], start=1):
            corrected = rec.get("corrected_fixture", {})
            mf = corrected.get("manufacturer") or rec.get("manufacturer", "")
            fx = corrected.get("fixture_name") or rec.get("fixture_name", "")
            note = rec.get("note", "")
            modes = corrected.get("modes", [])
            sample_channels = []
            if modes:
                for ch in modes[0].get("channels", [])[:12]:
                    sample_channels.append({
                        "channel": ch.get("channel"),
                        "name": ch.get("name"),
                        "attribute": ch.get("attribute"),
                        "resolution": ch.get("resolution"),
                        "fine_of": ch.get("fine_of"),
                        "head": ch.get("head"),
                    })
            parts.append(json.dumps({
                "example": i,
                "manufacturer": mf,
                "fixture": fx,
                "note": note,
                "confirmed_channel_mapping_sample": sample_channels,
            }, ensure_ascii=False, indent=2))
    return "\n\n".join(parts)
