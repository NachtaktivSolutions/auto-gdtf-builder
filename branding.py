from __future__ import annotations

import base64
from pathlib import Path
import streamlit as st


ASSET_DIR = Path(__file__).parent / "assets"


def asset_uri(filename: str) -> str:
    path = ASSET_DIR / filename
    if not path.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("utf-8")


def inject_brand_css() -> None:
    bg = asset_uri("background.png")
    css = f"""
    <style>
    :root {{
        --nas-bg: #08040f;
        --nas-card: rgba(16, 9, 28, 0.93);
        --nas-card-2: rgba(21, 12, 36, 0.97);
        --nas-line: rgba(225, 72, 255, 0.34);
        --nas-line-soft: rgba(225, 72, 255, 0.20);
        --nas-purple: #8b1cf6;
        --nas-magenta: #d127d6;
        --nas-pink: #ff55ef;
        --nas-text: #ffffff;
        --nas-muted: #d8d0e8;
        --nas-input-bg: #140d24;
        --nas-input-bg-focus: #1d1232;
        --nas-input-text: #ffffff;
        --nas-input-muted: #b9aecb;
        --nas-table-text: #1b0d29;
        --nas-uploader-bg: rgba(24, 14, 42, 0.96);
        --nas-uploader-file: rgba(255,255,255,0.10);
    }}

    .stApp {{
        background-color: var(--nas-bg);
        background-image: url("{bg}");
        background-size: cover;
        background-position: center top;
        background-attachment: fixed;
        color: var(--nas-text);
    }}

    [data-testid="stAppViewContainer"] > .main {{
        background: rgba(0, 0, 0, 0.08);
    }}

    .block-container {{
        max-width: 1320px;
        padding-top: 1.35rem;
        padding-bottom: 4rem;
    }}

    [data-testid="stSidebar"] {{
        background: rgba(8, 4, 15, 0.97);
        border-right: 1px solid var(--nas-line-soft);
    }}

    [data-testid="stSidebar"] * {{
        color: var(--nas-text) !important;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: var(--nas-text) !important;
        letter-spacing: -0.015em;
    }}

    p, span, label, div {{
        color: inherit;
    }}

    .nas-hero {{
        border: 1px solid var(--nas-line);
        border-radius: 28px;
        padding: 30px 34px;
        margin-bottom: 24px;
        background: linear-gradient(135deg, rgba(16, 9, 28, 0.95), rgba(26, 13, 45, 0.92));
        box-shadow: 0 22px 64px rgba(0, 0, 0, 0.38);
        backdrop-filter: blur(12px);
    }}

    .nas-hero-inner {{
        display: flex;
        align-items: center;
        gap: 34px;
    }}

    .nas-logo {{
        width: min(36vw, 365px);
        max-width: 365px;
        height: auto;
        filter: drop-shadow(0 10px 28px rgba(0,0,0,.35));
    }}

    .nas-hero-title {{
        font-size: clamp(2rem, 4vw, 4.1rem);
        line-height: .95;
        font-weight: 950;
        margin: 0;
        background: linear-gradient(90deg, #ff58ee 0%, #8b1cf6 90%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent !important;
        text-transform: uppercase;
        font-style: italic;
    }}

    .nas-hero-subtitle {{
        margin-top: 12px;
        color: var(--nas-muted) !important;
        font-size: 1.02rem;
        line-height: 1.45;
        max-width: 760px;
    }}

    .nas-badge-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 18px;
    }}

    .nas-badge {{
        border: 1px solid rgba(255,255,255,0.14);
        background: rgba(255,255,255,0.08);
        color: #fff !important;
        padding: 7px 12px;
        border-radius: 999px;
        font-size: .84rem;
    }}

    .nas-section-title {{
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 1.35rem;
        font-weight: 900;
        margin-bottom: 4px;
        color: var(--nas-text) !important;
    }}

    .nas-step {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        border-radius: 12px;
        font-weight: 900;
        background: linear-gradient(135deg, var(--nas-magenta), var(--nas-purple));
        box-shadow: 0 8px 22px rgba(139, 28, 246, .33);
        color: #fff !important;
        flex: 0 0 34px;
    }}

    .nas-section-caption {{
        color: var(--nas-muted) !important;
        margin: 2px 0 18px 44px;
        line-height: 1.45;
    }}

    [data-testid="stVerticalBlockBorderWrapper"] {{
        border: 1px solid var(--nas-line-soft) !important;
        border-radius: 22px !important;
        background: linear-gradient(180deg, rgba(16, 9, 28, .93), rgba(10, 6, 18, .93)) !important;
        box-shadow: 0 18px 45px rgba(0,0,0,.24);
        backdrop-filter: blur(10px);
        padding: 1.15rem 1.25rem !important;
    }}

    .stButton > button, .stDownloadButton > button {{
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,.16) !important;
        background: linear-gradient(135deg, #d127d6, #7f22ff) !important;
        color: #fff !important;
        font-weight: 850 !important;
        box-shadow: 0 12px 28px rgba(127, 34, 255, .24);
        min-height: 42px;
    }}

    .stButton > button:hover, .stDownloadButton > button:hover {{
        border-color: rgba(255,255,255,.36) !important;
        transform: translateY(-1px);
    }}

    .stTextInput label, .stTextArea label, .stSelectbox label,
    .stCheckbox label, .stSlider label, .stFileUploader label {{
        color: var(--nas-text) !important;
        font-weight: 750 !important;
    }}

    .stCaption, small, .stMarkdown p {{
        color: var(--nas-muted) !important;
    }}

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {{
        background-color: var(--nas-input-bg) !important;
        color: var(--nas-input-text) !important;
        -webkit-text-fill-color: var(--nas-input-text) !important;
        caret-color: #fff !important;
        border: 1px solid rgba(255,255,255,.22) !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }}

    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus {{
        background-color: var(--nas-input-bg-focus) !important;
        border-color: var(--nas-pink) !important;
        box-shadow: 0 0 0 1px rgba(255,85,239,.26) !important;
    }}

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {{
        color: var(--nas-input-muted) !important;
        opacity: 1 !important;
        -webkit-text-fill-color: var(--nas-input-muted) !important;
    }}

    div[data-baseweb="select"] > div {{
        background: var(--nas-input-bg) !important;
        color: var(--nas-input-text) !important;
        border: 1px solid rgba(255,255,255,.22) !important;
        border-radius: 12px !important;
    }}

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input {{
        color: var(--nas-input-text) !important;
        -webkit-text-fill-color: var(--nas-input-text) !important;
    }}

    .stCheckbox p {{
        color: var(--nas-text) !important;
        font-weight: 700 !important;
    }}

    /* Uploader: dropzone plus uploaded file pill */
    [data-testid="stFileUploader"] {{
        width: 100%;
    }}

    [data-testid="stFileUploader"] section {{
        position: relative;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 118px !important;
        padding: 18px !important;
        background: var(--nas-uploader-bg) !important;
        border: 2px dashed rgba(255, 85, 239, .68) !important;
        border-radius: 18px !important;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,.04);
    }}

    [data-testid="stFileUploader"] section:hover {{
        border-color: rgba(255, 85, 239, .95) !important;
        background: rgba(31, 18, 54, .98) !important;
    }}

    [data-testid="stFileUploader"] section * {{
        color: var(--nas-text) !important;
        fill: var(--nas-text) !important;
    }}

    [data-testid="stFileUploaderDropzoneInstructions"] {{
        display: flex !important;
        flex-direction: column !important;
        gap: 4px !important;
        text-align: center !important;
    }}

    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderDropzoneInstructions"] small {{
        color: var(--nas-text) !important;
    }}

    [data-testid="stFileUploader"] button {{
        background: linear-gradient(135deg, #d127d6, #7f22ff) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,.16) !important;
        border-radius: 12px !important;
        font-weight: 850 !important;
    }}

    /* Uploaded file row / pill in different Streamlit versions */
    [data-testid="stFileUploader"] ul,
    [data-testid="stFileUploader"] li,
    [data-testid="stFileUploaderFile"],
    [data-testid="stFileUploaderFileData"],
    [data-testid="stFileUploaderFileName"],
    [data-testid="stFileUploaderFileSize"] {{
        background: transparent !important;
        color: var(--nas-text) !important;
        -webkit-text-fill-color: var(--nas-text) !important;
    }}

    [data-testid="stFileUploader"] li,
    [data-testid="stFileUploaderFile"] {{
        background: var(--nas-uploader-file) !important;
        border: 1px solid rgba(255,255,255,.20) !important;
        border-radius: 14px !important;
        padding: 10px 12px !important;
        margin: 6px !important;
        display: flex !important;
        align-items: center !important;
        gap: 10px !important;
    }}

    [data-testid="stFileUploader"] svg {{
        color: var(--nas-text) !important;
        fill: var(--nas-text) !important;
    }}

    [data-testid="stFileUploader"] [aria-label="Delete"],
    [data-testid="stFileUploader"] [aria-label="Remove"] {{
        background: rgba(255,255,255,.08) !important;
        border: 1px solid rgba(255,255,255,.16) !important;
        border-radius: 999px !important;
    }}

    [data-testid="stExpander"] {{
        border: 1px solid rgba(225,72,255,.23) !important;
        border-radius: 14px !important;
        background: rgba(10, 6, 18, .55) !important;
        overflow: hidden;
    }}

    [data-testid="stExpander"] summary p {{
        color: var(--nas-text) !important;
        font-weight: 750 !important;
    }}

    [data-testid="stMetric"] {{
        border: 1px solid rgba(255,255,255,.12);
        background: rgba(255,255,255,.06);
        border-radius: 16px;
        padding: 14px 16px;
    }}

    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {{
        color: var(--nas-text) !important;
    }}

    [data-testid="stDataFrame"] *,
    [data-testid="stDataEditor"] * {{
        color: var(--nas-table-text) !important;
    }}

    [data-testid="stDataFrame"] [role="grid"],
    [data-testid="stDataEditor"] [role="grid"] {{
        background: #ffffff !important;
        border-radius: 14px !important;
        overflow: hidden !important;
    }}

    [data-testid="stDataEditor"] input,
    [data-testid="stDataEditor"] textarea {{
        color: var(--nas-table-text) !important;
        -webkit-text-fill-color: var(--nas-table-text) !important;
        background: #fff !important;
    }}

    [data-testid="stAlert"] {{
        border-radius: 14px !important;
    }}

    .nas-footer {{
        text-align: center;
        color: var(--nas-muted) !important;
        font-size: .86rem;
        padding: 28px 0 8px;
    }}

    @media (max-width: 850px) {{
        .nas-hero-inner {{
            flex-direction: column;
            align-items: flex-start;
        }}
        .nas-logo {{
            width: min(78vw, 340px);
        }}
        .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}
    }}

    /* v0.15 uploader hard fix */
    [data-testid="stFileUploader"] {
        width: 100% !important;
    }

    [data-testid="stFileUploader"] > div {
        width: 100% !important;
    }

    [data-testid="stFileUploader"] section {
        min-height: 138px !important;
        padding: 24px !important;
        background: linear-gradient(135deg, rgba(24,14,42,.98), rgba(34,18,58,.96)) !important;
        border: 2px dashed rgba(255,85,239,.82) !important;
        border-radius: 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 16px !important;
        overflow: visible !important;
    }

    [data-testid="stFileUploader"] section:hover {
        border-color: #ff55ef !important;
        background: linear-gradient(135deg, rgba(31,18,54,.99), rgba(42,23,72,.98)) !important;
    }

    [data-testid="stFileUploader"] section * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        fill: #ffffff !important;
    }

    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploader"] button[kind],
    [data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] {
        background: linear-gradient(135deg, #d127d6, #7f22ff) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 1px solid rgba(255,255,255,.24) !important;
        border-radius: 14px !important;
        min-width: 172px !important;
        min-height: 44px !important;
        padding: 0 18px !important;
        font-weight: 900 !important;
        box-shadow: 0 10px 26px rgba(127,34,255,.28) !important;
        opacity: 1 !important;
    }

    [data-testid="stFileUploader"] button p,
    [data-testid="stFileUploader"] button span,
    [data-testid="stFileUploader"] button div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 900 !important;
    }

    [data-testid="stFileUploaderDropzoneInstructions"] {
        display: flex !important;
        flex-direction: column !important;
        text-align: center !important;
        gap: 6px !important;
        max-width: 540px !important;
    }

    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderDropzoneInstructions"] small,
    [data-testid="stFileUploaderDropzoneInstructions"] div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
        font-weight: 700 !important;
    }

    /* Hide Streamlit's low-contrast internal selected-file pill.
       The app shows a custom readable upload status directly below the uploader. */
    [data-testid="stFileUploaderFile"],
    [data-testid="stFileUploaderFileData"],
    [data-testid="stFileUploaderFileName"],
    [data-testid="stFileUploaderFileSize"],
    [data-testid="stFileUploader"] ul,
    [data-testid="stFileUploader"] li {
        display: none !important;
    }

    .nas-upload-status {
        margin-top: 12px;
        padding: 12px 14px;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,.16);
        background: rgba(57, 217, 138, .12);
        color: #ffffff !important;
        font-weight: 750;
    }

    .nas-upload-status span {
        color: #39d98a !important;
        -webkit-text-fill-color: #39d98a !important;
        font-weight: 900;
    }

    .nas-reset-note {
        color: var(--nas-muted) !important;
        font-size: .86rem;
        margin-top: 6px;
    }

    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_sidebar_logo() -> None:
    logo = asset_uri("nachtaktiv_logo.png")
    if logo:
        st.sidebar.markdown(
            f"""
            <div style="text-align:center; padding: 10px 0 24px;">
                <img src="{logo}" style="max-width:210px; width:92%; height:auto;" />
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_hero(version: str) -> None:
    logo = asset_uri("nachtaktiv_logo.png")
    img = f'<img class="nas-logo" src="{logo}" />' if logo else ""
    st.markdown(
        f"""
        <div class="nas-hero">
            <div class="nas-hero-inner">
                {img}
                <div>
                    <div class="nas-hero-title">GDTF Builder</div>
                    <div class="nas-hero-subtitle">
                        Manual hochladen, DMX-Kanäle prüfen und sauber als GDTF, CSV oder JSON exportieren.
                    </div>
                    <div class="nas-badge-row">
                        <span class="nas-badge">v{version}</span>
                        <span class="nas-badge">Nachtaktiv Solutions</span>
                        <span class="nas-badge">B240 Template</span>
                        <span class="nas-badge">MA3 / Daslight / Wolfmix</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(number: int, title: str, caption: str = "") -> None:
    st.markdown(
        f"""
        <div class="nas-section-title"><span class="nas-step">{number}</span>{title}</div>
        <div class="nas-section-caption">{caption}</div>
        """,
        unsafe_allow_html=True,
    )
