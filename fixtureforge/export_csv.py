from __future__ import annotations
import csv, io
from .schema import Fixture

def fixture_to_channel_csv(fixture: Fixture, mode_name: str) -> bytes:
    mode = next(m for m in fixture.modes if m.name == mode_name)
    out = io.StringIO()
    writer = csv.writer(out, delimiter=";")
    writer.writerow(["Manufacturer", fixture.manufacturer])
    writer.writerow(["Fixture", fixture.fixture_name])
    writer.writerow(["Mode", mode.name])
    writer.writerow([])
    writer.writerow(["Channel", "Head", "Name", "Attribute", "Resolution", "Fine Of", "Default", "Snap", "Values"])
    for ch in mode.channels:
        values = " | ".join(f"{v.from_value}-{v.to_value}: {v.label}" for v in ch.values)
        writer.writerow([ch.channel, ch.head or "", ch.name, ch.attribute, ch.resolution, ch.fine_of or "", ch.default, ch.snap, values])
    return out.getvalue().encode("utf-8-sig")
