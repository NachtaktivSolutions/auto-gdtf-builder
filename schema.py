EXTRACTION_SCHEMA_DESCRIPTION = """
Return ONLY valid JSON with this structure:
{
  "manufacturer": "string",
  "fixture_name": "string",
  "notes": "string",
  "modes": [
    {
      "mode_name": "48CH",
      "channel_count": 48,
      "channels": [
        {
          "channel": 1,
          "fixture_part": "Head 1",
          "raw_name": "Horizontale Bewegung (PAN) 1",
          "attribute": "Pan",
          "resolution": "8bit|16bit_coarse|16bit_fine|virtual|unknown",
          "fine_for_channel": null,
          "default_dmx": 0,
          "highlight_dmx": null,
          "ranges": [
            {"from": 0, "to": 255, "name": "Pan", "type": "continuous", "comment": ""}
          ]
        }
      ]
    }
  ]
}
Rules:
- Include all DMX modes visible in the manual/sheet.
- Use integers for channel numbers and DMX ranges.
- Map German and English labels to console-friendly attributes.
- Attribute examples: Dimmer, Shutter, Strobe, Pan, Pan Fine, Tilt, Tilt Fine, PanTiltSpeed, ColorAdd_R, ColorAdd_G, ColorAdd_B, ColorAdd_W, ColorMacro, Macro, MacroSpeed, Reset, Gobo1, Gobo1Rotate, Prism, Zoom, Focus, Frost, Iris.
- For fine channels, set resolution to "16bit_fine" and fine_for_channel to the coarse channel number.
- If unsure, use attribute "Unknown" but keep raw_name and ranges.
"""
