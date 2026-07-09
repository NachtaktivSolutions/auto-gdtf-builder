# FixtureForge AI v0.10 – Working Streamlit Build

This build is designed to actually start on Streamlit Cloud.

Removed:
- Gemini
- RapidOCR
- OpenCV
- libGL dependency

Added:
- System Tesseract via `packages.txt`
- `pytesseract`
- Local PDF rendering with PyMuPDF
- Local OCR fallback
- Built-in Eurolite LED TMH Bar B240 parser/template
- Optional OpenRouter text-model analysis

## Streamlit Secrets

OpenRouter is optional in this version.

```toml
OPENROUTER_API_KEY = "sk-or-v1-..."
OPENROUTER_MODEL = "mistralai/mistral-small-3.2-24b-instruct:free"
```

If OpenRouter has no free credits/model, the built-in B240 parser still works for the B240 manual.

## Main file path

```text
streamlit_app.py
```


## v0.8 GDTF exporter changes

- Adds GDTF AttributeDefinitions
- Maps FixtureForge attributes to GDTF attributes
- Exports 16-bit Pan/Tilt as GDTF offsets like `1,2`
- Builds four beam geometries (`Head_1_Beam` ... `Head_4_Beam`) to help MA3 create fixture parts/subfixtures
- Adds ChannelFunctions and ChannelSets for DMX value ranges


## v0.9 Reference GDTF mode

For Eurolite LED TMH Bar B240 the app now exports a bundled reference GDTF:
`templates/eurolite_led_tmh_bar_b240_reference.gdtf`

This was added because grandMA3 recognized earlier generated GDTFs as a fixture shell but did not show useful parts/subfixtures. The reference template contains the more complete geometry / model / attribute / DMX mode structure.


## v0.10 Naming Polish

- Editable manufacturer / fixture name / short name / long name / export file prefix
- B240 channel labels normalized to `Head 1 Pan`, `Head 1 Dimmer`, etc.
- Mode names normalized to `4CH`, `8CH`, `13CH`, `15CH`, `23CH`, `27CH`, `40CH`, `48CH`
- Export filenames generated from the chosen file prefix
- Keeps the known-working B240 reference export path from v0.9
