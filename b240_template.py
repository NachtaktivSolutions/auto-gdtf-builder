from __future__ import annotations


def r_full(name="0-255", desc="0 bis 100 %"):
    return [{"from": 0, "to": 255, "name": name, "description": desc}]


def strobe_ranges():
    return [
        {"from": 0, "to": 10, "name": "No Function", "description": "Keine Funktion"},
        {"from": 11, "to": 255, "name": "Strobe", "description": "Strobe-Effekt mit zunehmender Geschwindigkeit"},
    ]


def reset_ranges():
    return [
        {"from": 0, "to": 230, "name": "No Function", "description": "Keine Funktion"},
        {"from": 231, "to": 249, "name": "Reset", "description": "Reset"},
        {"from": 250, "to": 255, "name": "No Function", "description": "Keine Funktion"},
    ]


def speed_music_ranges():
    return [
        {"from": 0, "to": 200, "name": "Speed fast to slow", "description": "Abnehmende Geschwindigkeit"},
        {"from": 201, "to": 255, "name": "Sound controlled", "description": "Musikgesteuert"},
    ]


def color_macro_ranges():
    base = [
        (0,4,"No Function"), (5,9,"1 Red, 2 Green, 3 Blue, 4 White"),
        (10,14,"1 Red, 2 Green, 3 Red, 4 Green"),
        (15,19,"1 Red, 2 Red, 3 Blue, 4 Blue"),
        (20,24,"1 Red, 2 White, 3 Red, 4 White"),
        (25,29,"1 Green, 2 Blue, 3 Green, 4 Blue"),
        (30,34,"1 White, 2 Green, 3 Green, 4 White"),
        (35,39,"1 Blue, 2 White, 3 Blue, 4 White"),
        (40,44,"All Red+Green"), (45,49,"All Red+Blue"), (50,54,"All Red+White"),
        (55,59,"All Green+Blue"), (60,64,"All Green+White"), (65,69,"All Blue+White"),
        (70,74,"All RGB"), (75,79,"All RGW"), (80,84,"All RBW"), (85,89,"All GBW"),
        (90,94,"All RGBW"),
    ]
    out = [{"from": a, "to": b, "name": n, "description": n} for a,b,n in base]
    for i, start in enumerate(range(155, 256, 5), start=1):
        out.append({"from": start, "to": min(start+4,255), "name": f"Program {i}", "description": f"Farbmakro Programm {i}"})
    return out


def movement_macro_ranges():
    out = [{"from": 0, "to": 9, "name": "No Function", "description": "Keine Funktion"}]
    positions = [
        (10,14,"Position 1"), (15,19,"Position 2"), (20,24,"Position 3"),
        (25,29,"Position 4"), (30,34,"Position 5"), (35,39,"Position 6"),
        (40,44,"Position 7"), (45,49,"Position 8"), (50,54,"Position 9"),
    ]
    out += [{"from": a, "to": b, "name": n, "description": n} for a,b,n in positions]
    labels = []
    for speed in ["slow", "medium", "fast", "sound"]:
        for p in range(1, 11):
            labels.append(f"Movement Program {p} {speed}")
    value = 55
    for label in labels:
        out.append({"from": value, "to": min(value+4,255), "name": label, "description": label})
        value += 5
        if value > 255:
            break
    return out


def head_select_ranges():
    return [
        {"from": 0, "to": 85, "name": "Heads 1&2 + 3&4", "description": "Spot 1&2 + 3&4 zusammen"},
        {"from": 86, "to": 170, "name": "Heads 1&3 + 2&4", "description": "Spot 1&3 + 2&4 zusammen"},
        {"from": 171, "to": 255, "name": "Heads 1&4 + 2&3", "description": "Spot 1&4 + 2&3 zusammen"},
    ]


def ch(channel, attribute, label, geometry=None, fine=None, ranges=None):
    return {
        "channel": channel,
        "fine_channel": fine,
        "attribute": attribute,
        "raw_label": label,
        "raw_description": label,
        "geometry": geometry,
        "default_value": None,
        "highlight_value": 255 if attribute == "Dimmer" else None,
        "ranges": ranges if ranges is not None else r_full()
    }


def head_channels(start, head_no, fine=True):
    g = f"Head {head_no}"
    if fine:
        return [
            ch(start, "Pan", f"PAN {head_no}", g, start+1),
            ch(start+1, "PanFine", f"PAN Fine {head_no}", g),
            ch(start+2, "Tilt", f"TILT {head_no}", g, start+3),
            ch(start+3, "TiltFine", f"TILT Fine {head_no}", g),
            ch(start+4, "PanTiltSpeed", f"PAN/TILT Speed {head_no}", g),
            ch(start+5, "Shutter", f"Strobe {head_no}", g, ranges=strobe_ranges()),
            ch(start+6, "Dimmer", f"Dimmer {head_no}", g),
            ch(start+7, "ColorAdd_R", f"Red {head_no}", g),
            ch(start+8, "ColorAdd_G", f"Green {head_no}", g),
            ch(start+9, "ColorAdd_B", f"Blue {head_no}", g),
            ch(start+10, "ColorAdd_W", f"White {head_no}", g),
        ]
    return [
        ch(start, "Pan", f"PAN {head_no}", g),
        ch(start+1, "Tilt", f"TILT {head_no}", g),
        ch(start+2, "PanTiltSpeed", f"PAN/TILT Speed {head_no}", g),
        ch(start+3, "Shutter", f"Strobe {head_no}", g, ranges=strobe_ranges()),
        ch(start+4, "Dimmer", f"Dimmer {head_no}", g),
        ch(start+5, "ColorAdd_R", f"Red {head_no}", g),
        ch(start+6, "ColorAdd_G", f"Green {head_no}", g),
        ch(start+7, "ColorAdd_B", f"Blue {head_no}", g),
        ch(start+8, "ColorAdd_W", f"White {head_no}", g),
    ]


def build_b240_fixture():
    fixture = {
        "manufacturer": "Eurolite",
        "fixture_name": "LED TMH Bar B240",
        "notes": "Built-in FixtureForge template based on Eurolite LED TMH Bar B240 manual. Modes 4/8/13/15/23/27/40/48 included.",
        "physical": {
            "pan_degrees": 540,
            "tilt_degrees": 180,
            "beam_angle_degrees": 2,
            "weight_kg": 12.9,
            "width_mm": 1000,
            "height_mm": 255,
            "depth_mm": 175,
        },
        "modes": [],
        "warnings": []
    }

    # 4CH
    fixture["modes"].append({"name": "4CH", "channel_count": 4, "confidence": 1.0, "channels": [
        ch(1, "Dimmer", "Dimmer"),
        ch(2, "PanTiltMacro", "Movement Macro", ranges=movement_macro_ranges()),
        ch(3, "ColorMacro", "Color Macro", ranges=color_macro_ranges()),
        ch(4, "MacroSpeed", "Speed and Sound Control", ranges=speed_music_ranges()),
    ]})

    # 8CH
    fixture["modes"].append({"name": "8CH", "channel_count": 8, "confidence": 1.0, "channels": [
        ch(1, "Dimmer", "Dimmer"),
        ch(2, "ColorAdd_R", "Red"),
        ch(3, "ColorAdd_G", "Green"),
        ch(4, "ColorAdd_B", "Blue"),
        ch(5, "ColorAdd_W", "White"),
        ch(6, "PanTiltMacro", "Movement Macro", ranges=movement_macro_ranges()),
        ch(7, "ColorMacro", "Color Macro", ranges=color_macro_ranges()),
        ch(8, "MacroSpeed", "Speed and Sound Control", ranges=speed_music_ranges()),
    ]})

    # 13CH
    fixture["modes"].append({"name": "13CH", "channel_count": 13, "confidence": 1.0, "channels": [
        ch(1, "Pan", "PAN"),
        ch(2, "Tilt", "TILT"),
        ch(3, "PanTiltSpeed", "PAN/TILT Speed"),
        ch(4, "Shutter", "Strobe", ranges=strobe_ranges()),
        ch(5, "Dimmer", "Dimmer"),
        ch(6, "ColorAdd_R", "Red"),
        ch(7, "ColorAdd_G", "Green"),
        ch(8, "ColorAdd_B", "Blue"),
        ch(9, "ColorAdd_W", "White"),
        ch(10, "PanTiltMacro", "Movement Macro", ranges=movement_macro_ranges()),
        ch(11, "ColorMacro", "Color Macro", ranges=color_macro_ranges()),
        ch(12, "MacroSpeed", "Speed and Sound Control", ranges=speed_music_ranges()),
        ch(13, "Reset", "Reset", ranges=reset_ranges()),
    ]})

    # 15CH
    fixture["modes"].append({"name": "15CH", "channel_count": 15, "confidence": 1.0, "channels": [
        ch(1, "Pan", "PAN", fine=2),
        ch(2, "PanFine", "PAN Fine"),
        ch(3, "Tilt", "TILT", fine=4),
        ch(4, "TiltFine", "TILT Fine"),
        ch(5, "PanTiltSpeed", "PAN/TILT Speed"),
        ch(6, "Shutter", "Strobe", ranges=strobe_ranges()),
        ch(7, "Dimmer", "Dimmer"),
        ch(8, "ColorAdd_R", "Red"),
        ch(9, "ColorAdd_G", "Green"),
        ch(10, "ColorAdd_B", "Blue"),
        ch(11, "ColorAdd_W", "White"),
        ch(12, "PanTiltMacro", "Movement Macro", ranges=movement_macro_ranges()),
        ch(13, "ColorMacro", "Color Macro", ranges=color_macro_ranges()),
        ch(14, "MacroSpeed", "Speed and Sound Control", ranges=speed_music_ranges()),
        ch(15, "Reset", "Reset", ranges=reset_ranges()),
    ]})

    # 23CH
    c23 = []
    c23 += head_channels(1, 1, fine=False)
    c23 += head_channels(10, 2, fine=False)
    c23 += [
        ch(19, "HeadSelect", "Head Selection", ranges=head_select_ranges()),
        ch(20, "PanTiltMacro", "Movement Macro", ranges=movement_macro_ranges()),
        ch(21, "ColorMacro", "Color Macro", ranges=color_macro_ranges()),
        ch(22, "MacroSpeed", "Speed and Sound Control", ranges=speed_music_ranges()),
        ch(23, "Reset", "Reset", ranges=reset_ranges()),
    ]
    fixture["modes"].append({"name": "23CH", "channel_count": 23, "confidence": 1.0, "channels": c23})

    # 27CH
    c27 = []
    c27 += head_channels(1, 1, fine=True)
    c27 += head_channels(12, 2, fine=True)
    c27 += [
        ch(23, "HeadSelect", "Head Selection", ranges=head_select_ranges()),
        ch(24, "PanTiltMacro", "Movement Macro", ranges=movement_macro_ranges()),
        ch(25, "ColorMacro", "Color Macro", ranges=color_macro_ranges()),
        ch(26, "MacroSpeed", "Speed and Sound Control", ranges=speed_music_ranges()),
        ch(27, "Reset", "Reset", ranges=reset_ranges()),
    ]
    fixture["modes"].append({"name": "27CH", "channel_count": 27, "confidence": 1.0, "channels": c27})

    # 40CH
    c40 = []
    c40 += head_channels(1, 1, fine=False)
    c40 += head_channels(10, 2, fine=False)
    c40 += head_channels(19, 3, fine=False)
    c40 += head_channels(28, 4, fine=False)
    c40 += [
        ch(37, "PanTiltMacro", "Movement Macro", ranges=movement_macro_ranges()),
        ch(38, "ColorMacro", "Color Macro", ranges=color_macro_ranges()),
        ch(39, "MacroSpeed", "Speed and Sound Control", ranges=speed_music_ranges()),
        ch(40, "Reset", "Reset", ranges=reset_ranges()),
    ]
    fixture["modes"].append({"name": "40CH", "channel_count": 40, "confidence": 1.0, "channels": c40})

    # 48CH
    c48 = []
    c48 += head_channels(1, 1, fine=True)
    c48 += head_channels(12, 2, fine=True)
    c48 += head_channels(23, 3, fine=True)
    c48 += head_channels(34, 4, fine=True)
    c48 += [
        ch(45, "PanTiltMacro", "Movement Macro", ranges=movement_macro_ranges()),
        ch(46, "ColorMacro", "Color Macro", ranges=color_macro_ranges()),
        ch(47, "MacroSpeed", "Speed and Sound Control", ranges=speed_music_ranges()),
        ch(48, "Reset", "Reset", ranges=reset_ranges()),
    ]
    fixture["modes"].append({"name": "48CH", "channel_count": 48, "confidence": 1.0, "channels": c48})

    return fixture


def looks_like_b240(filename: str = "", text: str = "") -> bool:
    s = f"{filename} {text}".lower()
    return ("b240" in s) or ("tmh bar b240" in s) or ("led tmh bar b240" in s)
