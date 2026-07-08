from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class ValueRange(BaseModel):
    from_value: int = Field(ge=0, le=255)
    to_value: int = Field(ge=0, le=255)
    label: str

class Channel(BaseModel):
    channel: int = Field(ge=1)
    name: str
    attribute: str
    head: Optional[int] = None
    resolution: str = "8bit"  # 8bit, coarse, fine
    fine_of: Optional[int] = None
    default: int = Field(default=0, ge=0, le=255)
    snap: bool = False
    values: List[ValueRange] = Field(default_factory=list)

class Mode(BaseModel):
    name: str
    channel_count: int = Field(ge=1, le=512)
    channels: List[Channel]

class Fixture(BaseModel):
    manufacturer: str = "Unknown"
    fixture_name: str = "Unknown Fixture"
    short_name: str = "Fixture"
    fixture_type: str = "Other"
    beam_angle_deg: Optional[float] = None
    pan_deg: Optional[float] = None
    tilt_deg: Optional[float] = None
    notes: str = ""
    modes: List[Mode]
