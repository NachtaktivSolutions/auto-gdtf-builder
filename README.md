# Nachtaktiv GDTF Builder v0.16 – Working Streamlit Build

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


## v0.16 GDTF exporter changes

- Adds GDTF AttributeDefinitions
- Maps FixtureForge attributes to GDTF attributes
- Exports 16-bit Pan/Tilt as GDTF offsets like `1,2`
- Builds four beam geometries (`Head_1_Beam` ... `Head_4_Beam`) to help MA3 create fixture parts/subfixtures
- Adds ChannelFunctions and ChannelSets for DMX value ranges


## v0.16 Reference GDTF mode

For Eurolite LED TMH Bar B240 the app now exports a bundled reference GDTF:
`templates/eurolite_led_tmh_bar_b240_reference.gdtf`

This was added because grandMA3 recognized earlier generated GDTFs as a fixture shell but did not show useful parts/subfixtures. The reference template contains the more complete geometry / model / attribute / DMX mode structure.


## v0.16 Naming Polish

- Editable manufacturer / fixture name / short name / long name / export file prefix
- B240 channel labels normalized to `Head 1 Pan`, `Head 1 Dimmer`, etc.
- Mode names normalized to `4CH`, `8CH`, `13CH`, `15CH`, `23CH`, `27CH`, `40CH`, `48CH`
- Export filenames generated from the chosen file prefix
- Keeps the known-working B240 reference export path from v0.16


## v0.16 CI / UI Cleanup

- Renamed app to **Nachtaktiv GDTF Builder**
- Added Nachtaktiv logo assets
- Added dark CI theme with magenta/purple gradients
- Added structured 7-step workflow
- Sidebar branding
- Clean cards/sections
- Better export naming
- Keeps B240 template/export functionality from previous versions


## v0.16 Clean Background + Readability

- App keeps Nachtaktiv CI but uses exactly one background image: `assets/background.png`
- Logo is separate: `assets/nachtaktiv_logo.png`
- Removed old multiple watermark/background assets
- All form fields now use bright background + dark text
- Labels, captions, expanders and data editor readability improved
- Same B240/GDTF functionality as before


## v0.16 Clean UI

- Broken fake card wrappers removed
- Real Streamlit bordered containers used
- One clean background image only: `assets/background.png`
- One logo file: `assets/nachtaktiv_logo.png`
- Upload field clearly visible
- Text fields dark, readable and CI-matching
- Reset button added in sidebar and top right
- Same B240/GDTF functionality as before


## v0.16 Upload + Reset Fix

- File uploader contrast fixed after a file is uploaded
- Uploader dropzone alignment improved
- Reset now really clears file_uploader by changing widget keys
- Reset clears upload, text fields, checkboxes, editors, fixture state and export state
- Background remains one clean image: `assets/background.png`
- Logo remains one file: `assets/nachtaktiv_logo.png`


## v0.16 Stable from v0.14

This version intentionally reverts the risky v0.15 reset implementation.

- Based on stable v0.14
- Upload dropzone and uploaded file pill contrast improved
- Custom readable upload status added below uploader
- Reset uses simple state clear + incrementing file_uploader key
- No query_params manipulation
- No cache clearing
- No hidden uploader internals
