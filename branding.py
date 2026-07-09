from __future__ import annotations

import base64
from pathlib import Path
import streamlit as st


ASSET_DIR = Path(__file__).parent / "assets"


def asset_uri(filename: str) -> str:
    path = ASSET_DIR / filename
    if not path.exists():
        return ""
    data = path.read_bytes()
    mime = "image/png"
    return f"data:{mime};base64," + base64.b64encode(data).decode("utf-8")


def inject_brand_css() -> None:
    bg = asset_uri("background.png")
    css = f"""
    <style>
    :root {{
        --nas-bg: #07020d;
        --nas-panel: rgba(18, 10, 31, 0.92);
        --nas-panel-solid: #171020;
        --nas-border: rgba(225, 70, 255, 0.28);
        --nas-border-strong: rgba(255, 92, 235, 0.46);
        --nas-purple: #8b1cf6;
        --nas-magenta: #d127d6;
        --nas-pink: #ff55ef;
        --nas-text: #ffffff;
        --nas-muted: #d9d0ea;
        --nas-input-bg: #fbf8ff;
        --nas-input-text: #15091f;
    }}

    .stApp {{
        background-color: var(--nas-bg);
        background-image: url("{bg}");
        background-size: cover;
        background-position: center center;
        background-attachment: fixed;
        color: var(--nas-text);
    }}

    [data-testid="stAppViewContainer"] > .main {{
        background: linear-gradient(90deg, rgba(5,2,9,0.18), rgba(5,2,9,0.08));
    }}

    [data-testid="stSidebar"] {{
        background: rgba(9, 4, 17, 0.96);
        border-right: 1px solid var(--nas-border);
    }}

    [data-testid="stSidebar"] * {{
        color: var(--nas-text);
    }}

    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 3.5rem;
        max-width: 1380px;
    }}

    h1, h2, h3, h4, h5, h6, p, span, label, div {{
        color: inherit;
    }}

    .nas-hero {{
        border: 1px solid var(--nas-border);
        border-radius: 28px;
        padding: 34px 38px;
        margin-bottom: 24px;
        background: linear-gradient(135deg, rgba(15, 8, 27, 0.94), rgba(31, 14, 53, 0.90));
        box-shadow: 0 22px 70px rgba(0, 0, 0, 0.42);
        backdrop-filter: blur(12px);
    }}

    .nas-hero-inner {{
        display: flex;
        align-items: center;
        gap: 30px;
    }}

    .nas-logo {{
        max-width: 390px;
        width: min(38vw, 390px);
        height: auto;
        display: block;
        filter: drop-shadow(0 10px 30px rgba(0,0,0,.35));
    }}

    .nas-hero-title {{
        font-size: clamp(2.1rem, 4vw, 4.25rem);
        line-height: 0.95;
        font-weight: 950;
        margin: 0;
        background: linear-gradient(90deg, #ff4fe9 0%, #8b1cf6 88%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        text-transform: uppercase;
        font-style: italic;
        letter-spacing: -0.035em;
    }}

    .nas-hero-subtitle {{
        margin-top: 12px;
        color: var(--nas-muted);
        font-size: 1.06rem;
        max-width: 760px;
        line-height: 1.45;
    }}

    .nas-badge-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 18px;
    }}

    .nas-badge {{
        border: 1px solid rgba(255,255,255,0.14);
        background: rgba(255,255,255,0.09);
        color: #fff;
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 0.84rem;
        backdrop-filter: blur(10px);
    }}

    .nas-card {{
        border: 1px solid var(--nas-border);
        border-radius: 20px;
        padding: 21px 23px;
        background: linear-gradient(180deg, rgba(18, 10, 31, 0.94), rgba(12, 7, 22, 0.94));
        box-shadow: 0 14px 45px rgba(0,0,0,0.24);
        margin: 16px 0 22px 0;
        backdrop-filter: blur(10px);
    }}

    .nas-step {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 34px;
        height: 34px;
        border-radius: 12px;
        margin-right: 10px;
        font-weight: 850;
        background: linear-gradient(135deg, var(--nas-magenta), var(--nas-purple));
        color: white;
        box-shadow: 0 8px 24px rgba(139, 28, 246, 0.35);
    }}

    .nas-section-title {{
        display: flex;
        align-items: center;
        font-weight: 900;
        font-size: 1.35rem;
        margin-bottom: 8px;
        color: var(--nas-text);
    }}

    .nas-section-caption {{
        color: var(--nas-muted);
        margin-bottom: 16px;
        line-height: 1.45;
    }}

    /* Buttons */
    .stButton > button, .stDownloadButton > button {{
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.14) !important;
        background: linear-gradient(135deg, #d127d6, #7f22ff) !important;
        color: white !important;
        font-weight: 800 !important;
        box-shadow: 0 12px 28px rgba(127, 34, 255, 0.27);
    }}

    .stButton > button:hover, .stDownloadButton > button:hover {{
        border-color: rgba(255,255,255,0.34) !important;
        transform: translateY(-1px);
    }}

    /* File uploader */
    [data-testid="stFileUploader"] section {{
        border-radius: 18px;
        border: 1px dashed rgba(255, 85, 239, 0.50);
        background: rgba(255,255,255,0.055);
    }}

    [data-testid="stFileUploader"] section * {{
        color: var(--nas-text) !important;
    }}

    /* Labels and help text */
    .stTextInput label, .stTextArea label, .stSelectbox label,
    .stCheckbox label, .stSlider label, .stFileUploader label {{
        color: var(--nas-text) !important;
        font-weight: 700 !important;
    }}

    .stCaption, small, .stMarkdown p {{
        color: var(--nas-muted) !important;
    }}

    /* Inputs: readable white fields */
    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {{
        background: var(--nas-input-bg) !important;
        color: var(--nas-input-text) !important;
        border: 1px solid rgba(0,0,0,0.10) !important;
        border-radius: 12px !important;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.45);
    }}

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {{
        color: #6e607e !important;
        opacity: 1 !important;
    }}

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input {{
        color: var(--nas-input-text) !important;
    }}

    /* Checkbox text */
    .stCheckbox p {{
        color: var(--nas-text) !important;
        font-weight: 650 !important;
    }}

    /* Expanders */
    [data-testid="stExpander"] {{
        border: 1px solid rgba(225,70,255,0.26);
        border-radius: 14px;
        background: rgba(8, 4, 15, 0.44);
    }}

    [data-testid="stExpander"] summary p {{
        color: var(--nas-text) !important;
        font-weight: 750 !important;
    }}

    /* Metrics */
    [data-testid="stMetric"] {{
        background: rgba(255,255,255,0.075);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        padding: 16px;
    }}

    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {{
        color: var(--nas-text) !important;
    }}

    /* Data editor readability */
    [data-testid="stDataFrame"] *,
    [data-testid="stDataEditor"] * {{
        color: #17091f !important;
    }}

    [data-testid="stDataFrame"] [role="grid"],
    [data-testid="stDataEditor"] [role="grid"] {{
        background: rgba(255,255,255,0.98) !important;
        border-radius: 14px !important;
        overflow: hidden;
    }}

    [data-testid="stDataFrame"] thead *,
    [data-testid="stDataEditor"] thead * {{
        color: #2b1740 !important;
        font-weight: 800 !important;
    }}

    [data-testid="stDataEditor"] input,
    [data-testid="stDataEditor"] textarea {{
        color: #17091f !important;
        background: #ffffff !important;
    }}

    /* Alerts */
    [data-testid="stAlert"] {{
        border-radius: 16px;
    }}

    .nas-footer {{
        color: var(--nas-muted);
        text-align: center;
        font-size: 0.86rem;
        padding: 28px 0 10px 0;
    }}

    @media (max-width: 850px) {{
        .nas-hero-inner {{
            flex-direction: column;
            align-items: flex-start;
        }}
        .nas-logo {{
            width: min(76vw, 340px);
        }}
        .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_sidebar_logo() -> None:
    logo = asset_uri("nachtaktiv_logo.png")
    if logo:
        st.sidebar.markdown(
            f"""
            <div style="text-align:center; padding: 12px 4px 24px 4px;">
                <img src="{logo}" style="max-width:190px; width:90%; height:auto;" />
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
                        Fixture-Generator für MA3, Daslight & Wolfmix. Manual hochladen, Kanäle prüfen und sauber als GDTF, CSV oder JSON exportieren.
                    </div>
                    <div class="nas-badge-row">
                        <span class="nas-badge">v{version}</span>
                        <span class="nas-badge">Nachtaktiv Solutions</span>
                        <span class="nas-badge">B240 Template</span>
                        <span class="nas-badge">GDTF / CSV / JSON</span>
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


def open_card() -> None:
    st.markdown('<div class="nas-card">', unsafe_allow_html=True)


def close_card() -> None:
    st.markdown('</div>', unsafe_allow_html=True)
