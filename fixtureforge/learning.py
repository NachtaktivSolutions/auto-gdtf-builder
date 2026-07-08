from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from .schema import Fixture

DATA_DIR = Path("training_data")
DATA_DIR.mkdir(exist_ok=True)

def save_training_example(original: dict, corrected: Fixture, note: str = "") -> Path:
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = DATA_DIR / f"training_{ts}.json"
    payload = {
        "created_utc": ts,
        "note": note,
        "original_ai_result": original,
        "corrected_fixture": corrected.model_dump(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
