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
    return "data:image/png;base64," + base64.b64encode(data).decode("utf-8")


def inject_brand_css() -> None:
    watermark = asset_uri("wolf_watermark_5.png")
    css = f"""
    <style>
    :root {{
        --nas-bg: #08050f;
        --nas-panel: rgba(18, 13, 29, 0.86);
        --nas-panel-2: rgba(25, 18, 42, 0.92);
        --nas-border: rgba(190, 60, 255, 0.24);
        --nas-purple: #8b1cf6;
        --nas-magenta: #d127d6;
        --nas-gold: #2c1900;
        --nas-text: #f7f3ff;
        --nas-muted: #bcb2cc;
        --nas-success: #39d98a;
        --nas-warning: #ffcc66;
    }}

    .stApp {{
        background:
            radial-gradient(circle at 18% 12%, rgba(210, 39, 214, 0.22) 0, rgba(210, 39, 214, 0.06) 22%, transparent 42%),
            radial-gradient(circle at 82% 8%, rgba(139, 28, 246, 0.23) 0, rgba(139, 28, 246, 0.07) 23%, transparent 46%),
            linear-gradient(135deg, #07040d 0%, #10071d 50%, #050308 100%);
        color: var(--nas-text);
    }}

    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        background-image: url("{watermark}");
        background-size: min(72vw, 900px);
        background-repeat: no-repeat;
        background-position: right -120px bottom -160px;
        opacity: 0.16;
        pointer-events: none;
        z-index: 0;
    }}

    [data-testid="stAppViewContainer"] > .main {{
        position: relative;
        z-index: 1;
    }}

    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(12, 7, 20, 0.96), rgba(18, 9, 30, 0.96));
        border-right: 1px solid var(--nas-border);
    }}

    [data-testid="stSidebar"] * {{
        color: var(--nas-text);
    }}

    .block-container {{
        padding-top: 1.8rem;
        padding-bottom: 4rem;
        max-width: 1280px;
    }}

    h1, h2, h3 {{
        color: var(--nas-text);
        letter-spacing: -0.02em;
    }}

    .nas-hero {{
        position: relative;
        overflow: hidden;
        border: 1px solid var(--nas-border);
        border-radius: 28px;
        padding: 34px 38px;
        margin-bottom: 28px;
        background:
            linear-gradient(135deg, rgba(13, 8, 24, 0.92), rgba(27, 12, 48, 0.86)),
            radial-gradient(circle at 15% 20%, rgba(209, 39, 214, 0.28), transparent 38%),
            radial-gradient(circle at 85% 10%, rgba(139, 28, 246, 0.24), transparent 40%);
        box-shadow: 0 22px 70px rgba(0, 0, 0, 0.42);
    }}

    .nas-hero::after {{
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(110deg, transparent 0%, rgba(255,255,255,0.06) 42%, transparent 54%);
        transform: translateX(-60%);
        opacity: 0.55;
        pointer-events: none;
    }}

    .nas-hero-inner {{
        position: relative;
        z-index: 2;
        display: flex;
        align-items: center;
        gap: 28px;
    }}

    .nas-logo {{
        max-width: 360px;
        width: min(38vw, 360px);
        height: auto;
        display: block;
    }}

    .nas-hero-title {{
        font-size: clamp(2rem, 4vw, 4.2rem);
        line-height: 0.95;
        font-weight: 900;
        margin: 0;
        background: linear-gradient(90deg, #ff39df 0%, #8b1cf6 85%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        text-transform: uppercase;
        font-style: italic;
    }}

    .nas-hero-subtitle {{
        margin-top: 12px;
        color: var(--nas-muted);
        font-size: 1.03rem;
        max-width: 680px;
    }}

    .nas-badge-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 18px;
    }}

    .nas-badge {{
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.07);
        color: #fff;
        padding: 7px 11px;
        border-radius: 999px;
        font-size: 0.82rem;
        backdrop-filter: blur(10px);
    }}

    .nas-card {{
        border: 1px solid var(--nas-border);
        border-radius: 20px;
        padding: 20px 22px;
        background: var(--nas-panel);
        box-shadow: 0 14px 45px rgba(0,0,0,0.22);
        margin: 16px 0 22px 0;
    }}

    .nas-card h2, .nas-card h3 {{
        margin-top: 0;
    }}

    .nas-step {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 34px;
        height: 34px;
        border-radius: 12px;
        margin-right: 10px;
        font-weight: 800;
        background: linear-gradient(135deg, var(--nas-magenta), var(--nas-purple));
        color: white;
        box-shadow: 0 8px 24px rgba(139, 28, 246, 0.35);
    }}

    .nas-section-title {{
        display: flex;
        align-items: center;
        font-weight: 850;
        font-size: 1.35rem;
        margin-bottom: 8px;
        color: var(--nas-text);
    }}

    .nas-section-caption {{
        color: var(--nas-muted);
        margin-bottom: 16px;
    }}

    .stButton > button, .stDownloadButton > button {{
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.13) !important;
        background: linear-gradient(135deg, #d127d6, #7f22ff) !important;
        color: white !important;
        font-weight: 750 !important;
        box-shadow: 0 12px 28px rgba(127, 34, 255, 0.27);
    }}

    .stButton > button:hover, .stDownloadButton > button:hover {{
        border-color: rgba(255,255,255,0.34) !important;
        transform: translateY(-1px);
    }}

    [data-testid="stFileUploader"] section {{
        border-radius: 18px;
        border: 1px dashed rgba(209, 39, 214, 0.45);
        background: rgba(255,255,255,0.045);
    }}

    textarea, input, [data-baseweb="input"] {{
        border-radius: 12px !important;
    }}

    [data-testid="stExpander"] {{
        border: 1px solid rgba(190,60,255,0.22);
        border-radius: 14px;
        background: rgba(255,255,255,0.035);
    }}

    [data-testid="stMetric"] {{
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 16px;
    }}

    .nas-footer {{
        color: var(--nas-muted);
        text-align: center;
        font-size: 0.85rem;
        padding: 26px 0 10px 0;
    }}

    @media (max-width: 800px) {{
        .nas-hero-inner {{
            flex-direction: column;
            align-items: flex-start;
        }}
        .nas-logo {{
            width: min(72vw, 320px);
        }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_sidebar_logo() -> None:
    logo = asset_uri("logo_wolf.png")
    if logo:
        st.sidebar.markdown(
            f"""
            <div style="text-align:center; padding: 12px 4px 24px 4px;">
                <img src="{logo}" style="max-width:120px; opacity:.95;" />
                <div style="margin-top:12px; font-weight:900; letter-spacing:.02em;">NACHTAKTIV</div>
                <div style="color:#bcb2cc; font-size:.82rem;">GDTF Builder</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_hero(version: str) -> None:
    logo = asset_uri("nachtaktiv_full_logo.png") or asset_uri("logo_wolf.png")
    img = f'<img class="nas-logo" src="{logo}" />' if logo else ""
    st.markdown(
        f"""
        <div class="nas-hero">
            <div class="nas-hero-inner">
                {img}
                <div>
                    <div class="nas-hero-title">GDTF Builder</div>
                    <div class="nas-hero-subtitle">
                        Fixture-Generator für MA3, Daslight & Wolfmix. Manual rein, Kanäle prüfen, GDTF sauber exportieren.
                    </div>
                    <div class="nas-badge-row">
                        <span class="nas-badge">v{version}</span>
                        <span class="nas-badge">Nachtaktiv Solutions CI</span>
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
