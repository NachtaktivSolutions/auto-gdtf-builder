from __future__ import annotations

import io
import pandas as pd
from typing import Any, Dict


def mode_to_dataframe(mode: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    for ch in mode.get("channels", []):
        ranges = ch.get("ranges") or []
        ranges_txt = " | ".join([f"{r.get('from')}-{r.get('to')}: {r.get('name')}" for r in ranges])
        rows.append({
            "channel": ch.get("channel"),
            "fine_channel": ch.get("fine_channel"),
            "attribute": ch.get("attribute"),
            "raw_label": ch.get("raw_label"),
            "raw_description": ch.get("raw_description"),
            "geometry": ch.get("geometry"),
            "ranges": ranges_txt,
        })
    return pd.DataFrame(rows)


def fixture_to_csv_bytes(fixture: Dict[str, Any]) -> bytes:
    output = io.StringIO()
    for mode in fixture.get("modes", []):
        output.write(f"# Mode: {mode.get('name')} ({mode.get('channel_count')}CH)\n")
        df = mode_to_dataframe(mode)
        output.write(df.to_csv(index=False))
        output.write("\n")
    return output.getvalue().encode("utf-8")
