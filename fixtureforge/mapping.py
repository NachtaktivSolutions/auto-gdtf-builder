CANONICAL_ATTRIBUTES = {
    "pan": "Pan",
    "horizontal": "Pan",
    "horizontale bewegung": "Pan",
    "pan fine": "PanFine",
    "tilt": "Tilt",
    "vertical": "Tilt",
    "vertikale bewegung": "Tilt",
    "tilt fine": "TiltFine",
    "dimmer": "Dimmer",
    "intensity": "Dimmer",
    "strobe": "Strobe",
    "shutter": "Shutter",
    "red": "Red",
    "rot": "Red",
    "green": "Green",
    "grün": "Green",
    "blue": "Blue",
    "blau": "Blue",
    "white": "White",
    "weiß": "White",
    "macro": "Macro",
    "makro": "Macro",
    "speed": "MacroSpeed",
    "reset": "Reset",
}

def normalize_attribute(value: str) -> str:
    key = (value or "").strip().lower()
    for k, v in CANONICAL_ATTRIBUTES.items():
        if k in key:
            return v
    return value or "Unknown"
