import json
from datetime import datetime


def make_learning_record(original_fixture: dict, corrected_fixture: dict) -> bytes:
    record = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "type": "fixture_correction",
        "original": original_fixture,
        "corrected": corrected_fixture,
    }
    return json.dumps(record, ensure_ascii=False, indent=2).encode("utf-8")
