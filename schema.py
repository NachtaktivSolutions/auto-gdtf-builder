"""Interne Datenstruktur fuer den KI-zu-GDTF-Workflow.

Die KI soll NIE direkt GDTF-XML schreiben. Sie soll dieses JSON fuellen.
Der Generator baut daraus deterministisch eine .gdtf-Datei.
"""

FIXTURE_JSON_EXAMPLE = {
    "manufacturer": "Eurolite",
    "fixture_name": "LED TMH Bar B240",
    "short_name": "TMH Bar B240",
    "notes": ["Example structure"],
    "physical": {
        "pan_degrees": 540,
        "tilt_degrees": 180,
        "beam_angle_degrees": 2,
        "lamp_type": "LED",
        "colors": ["Red", "Green", "Blue", "White"]
    },
    "modes": [
        {
            "name": "48CH",
            "channel_count": 48,
            "channels": [
                {
                    "channel": 1,
                    "geometry": "Head 1",
                    "attribute": "Pan",
                    "function": "Pan coarse",
                    "resolution": "coarse",
                    "fine_channel": 2,
                    "default": 128,
                    "ranges": [{"from": 0, "to": 255, "name": "Pan 0-540"}]
                },
                {
                    "channel": 3,
                    "geometry": "Head 1",
                    "attribute": "Tilt",
                    "function": "Tilt coarse",
                    "resolution": "coarse",
                    "fine_channel": 4,
                    "default": 128,
                    "ranges": [{"from": 0, "to": 255, "name": "Tilt 0-180"}]
                }
            ]
        }
    ]
}

ALLOWED_ATTRIBUTES = [
    "Dimmer", "Shutter", "Strobe", "Pan", "Tilt", "PanTiltSpeed",
    "ColorAdd_R", "ColorAdd_G", "ColorAdd_B", "ColorAdd_W", "ColorMacro",
    "Macro", "MacroSpeed", "Reset", "NoFunction", "Gobo", "GoboRotate",
    "Prism", "PrismRotate", "Zoom", "Focus", "Frost", "Iris", "Unknown"
]

ATTRIBUTE_HINTS = {
    "pan": "Pan",
    "horizontale bewegung": "Pan",
    "tilt": "Tilt",
    "vertikale bewegung": "Tilt",
    "dimmer": "Dimmer",
    "dimmerintensität": "Dimmer",
    "strobe": "Strobe",
    "shutter": "Shutter",
    "rot": "ColorAdd_R",
    "red": "ColorAdd_R",
    "grün": "ColorAdd_G",
    "green": "ColorAdd_G",
    "blau": "ColorAdd_B",
    "blue": "ColorAdd_B",
    "weiß": "ColorAdd_W",
    "white": "ColorAdd_W",
    "farbmakro": "ColorMacro",
    "color macro": "ColorMacro",
    "bewegungsmakro": "Macro",
    "macro": "Macro",
    "speed": "MacroSpeed",
    "geschwindigkeit": "MacroSpeed",
    "reset": "Reset",
}
