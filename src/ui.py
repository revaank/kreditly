from __future__ import annotations

"""Branding, shared page chrome and reusable display components."""
import streamlit as st
import plotly.graph_objects as go
from .translations import t
from .finance import format_inr, loan_summary

CSS="""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Mukta:wght@400;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
  --bg: #F5F6F1;
  --ink: #0F1B15;
  --muted: #4A554F;
  --line: #E2E5DC;
  --card: #FFFFFF;
  --soft: #EEF0EA;
  --accent: #C6F24E;
  --good: #1F7A4D;
  --warn: #B7791F;
  --bad: #B5523B;
  --tint-good: #E7F4DD;
  --tint-warn: #FDF1DC;
  --tint-bad: #FBE7E2;
  --navy: var(--ink);
  --lime: var(--accent);
  --emerald: var(--good);
  --amber: var(--warn);
  --red: var(--bad);
}

html, body, [class*="css"] {
  font-family: 'Inter', 'Mukta', system-ui, sans-serif;
  color: var(--ink);
  margin: 0;
}

body {
  background: #F5F6F1;
}

/* Page background: soft glow + faint dot grid */
.stApp {
  background:
    radial-gradient(900px 520px at 82% 8%, rgba(198,242,78,.28), transparent 60%),
    radial-gradient(700px 480px at 4% 38%, rgba(31,122,77,.08), transparent 62%),
    radial-gradient(800px 600px at 96% 78%, rgba(198,242,78,.14), transparent 60%),
    #F5F6F1 !important;
  background-attachment: fixed !important;
  color: var(--ink);
}

.stApp::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image: radial-gradient(rgba(15,27,21,.10) 1px, transparent 1.2px);
  background-size: 22px 22px;
  -webkit-mask-image: linear-gradient(to bottom, #000 0%, rgba(0,0,0,.55) 35%, transparent 70%);
  mask-image: linear-gradient(to bottom, #000 0%, rgba(0,0,0,.55) 35%, transparent 70%);
  z-index: 0;
}

/* Make ALL Streamlit wrappers transparent */
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main,
.block-container,
[data-testid="stHeader"],
[data-testid="stVerticalBlock"],
[data-testid="stMarkdownContainer"] {
  background: transparent !important;
  box-shadow: none !important;
  border: none !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
  background: transparent;
  border: none;
  box-shadow: none;
}
div[data-testid="stVerticalBlockBorderWrapper"]:not([style*="border"]) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

div[data-testid="column"] {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
div[data-testid="column"] > div {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

.block-container {
  position: relative;
  z-index: 1;
  max-width: 1264px !important;
  padding-top: 0 !important;
  padding-left: 32px !important;
  padding-right: 32px !important;
  padding-bottom: 24px !important;
}

div[data-testid="stMarkdownContainer"] > p {
  margin: 0 !important;
}

/* Link overrides */
[data-testid="stMarkdownContainer"] a, [data-testid="stMarkdownContainer"] a:visited {
  color: inherit !important;
  text-decoration: none !important;
}
[data-testid="stMarkdownContainer"] a * {
  text-decoration: none !important;
}

#MainMenu, footer[data-testid="stFooter"], .stApp > footer {
  visibility: hidden !important;
}
.kd-footer {
  visibility: visible !important;
  display: flex !important;
}

header[data-testid="stHeader"] {
  background: transparent !important;
}

[data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] {
  display: none !important;
}

/* Typography */
h1, h2, h3, h4, h5, h6, .sg {
  font-family: 'Space Grotesk', 'Mukta', sans-serif !important;
  color: var(--ink) !important;
  letter-spacing: -0.025em;
}

small, .muted, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
  color: var(--muted) !important;
}

/* Header */
div[data-testid="stHorizontalBlock"]:has(.hdr-nav) {
  max-width: 1200px !important;
  margin: 0 auto !important;
  padding: 22px 32px !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
div[data-testid="stHorizontalBlock"]:has(.hdr-nav) > div[data-testid="column"] {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
div[data-testid="stHorizontalBlock"]:has(.hdr-nav) [data-testid="stVerticalBlock"] {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

.hdr-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 34px;
  flex-wrap: nowrap;
}
.hdr-nav a {
  font-size: 15px !important;
  font-weight: 500 !important;
  line-height: 1 !important;
  text-decoration: none !important;
  color: #4A554F !important;
  transition: color 0.15s ease;
  white-space: nowrap !important;
}
.hdr-nav a:hover {
  color: #0F1B15 !important;
}
.hdr-nav a.active {
  color: #0F1B15 !important;
  font-weight: 600 !important;
  border-bottom: 2px solid #0F1B15 !important;
  padding-bottom: 4px !important;
}

/* Header Language pill */
.hdr-lang-wrap {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
.hdr-lang-wrap div[data-testid="stButton"] {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  width: auto !important;
}
.hdr-lang-wrap button {
  background: #FFFFFF !important;
  border: 1px solid #E2E5DC !important;
  border-radius: 999px !important;
  padding: 3px !important;
  min-height: 34px !important;
  height: 34px !important;
  width: auto !important;
  min-width: 96px !important;
  box-shadow: none !important;
  cursor: pointer !important;
  white-space: nowrap !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}
.hdr-lang-wrap button:hover {
  border-color: #CBD0C5 !important;
  background: #FFFFFF !important;
}
.hdr-lang-wrap button p {
  color: #4A554F !important;
  margin: 0 !important;
  padding: 0 4px !important;
  font-size: 13px !important;
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 4px !important;
  white-space: nowrap !important;
}
.hdr-lang-wrap button strong {
  background: #0F1B15 !important;
  color: #FFFFFF !important;
  border-radius: 999px !important;
  padding: 6px 12px !important;
  font-weight: 600 !important;
  font-size: 13px !important;
  display: inline-block !important;
  white-space: nowrap !important;
  line-height: 1 !important;
}

/* Buttons */
button[data-testid="baseButton-primary"] {
  background-color: var(--accent) !important;
  color: var(--ink) !important;
  font-weight: 700 !important;
  font-family: 'Space Grotesk', 'Inter', sans-serif !important;
  border: 1px solid var(--accent) !important;
  border-radius: 14px !important;
  height: 48px !important;
  min-height: 48px !important;
  box-shadow: 0 4px 14px rgba(198, 242, 78, 0.4) !important;
  transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}
button[data-testid="baseButton-primary"]:hover {
  background-color: #BBEB44 !important;
  border-color: #BBEB44 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 18px rgba(198, 242, 78, 0.5) !important;
}
button[data-testid="baseButton-secondary"] {
  background-color: #FFFFFF !important;
  color: var(--ink) !important;
  font-weight: 600 !important;
  font-family: 'Inter', 'Mukta', sans-serif !important;
  border: 1px solid var(--line) !important;
  border-radius: 14px !important;
  height: 48px !important;
  min-height: 48px !important;
  box-shadow: none !important;
  transition: background 0.15s ease, border-color 0.15s ease !important;
}
button[data-testid="baseButton-secondary"]:hover {
  background-color: #F8F9F6 !important;
  border-color: #CBD0C5 !important;
}

/* Pills / Segmented Controls / Chips */
div[data-testid="stSegmentedControl"] button,
div[data-testid="stPills"] button {
  border-radius: 999px !important;
  border: 1px solid var(--line) !important;
  background-color: #FFFFFF !important;
  color: var(--muted) !important;
  height: 38px !important;
  min-height: 38px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  padding: 0 16px !important;
  transition: all 0.15s ease !important;
}
div[data-testid="stSegmentedControl"] button:hover,
div[data-testid="stPills"] button:hover {
  border-color: #CBD0C5 !important;
  color: var(--ink) !important;
}
div[data-testid="stSegmentedControl"] button[aria-selected="true"],
div[data-testid="stPills"] button[aria-selected="true"] {
  background-color: #F1F9DF !important;
  border: 2px solid var(--ink) !important;
  color: var(--ink) !important;
  font-weight: 700 !important;
}

/* Results section switcher pill styling: ink pill with white text when selected */
.results-nav-wrapper div[data-testid="stSegmentedControl"] button[aria-selected="true"],
.results-nav-wrapper div[data-testid="stPills"] button[aria-selected="true"] {
  background-color: #0F1B15 !important;
  border: 1px solid #0F1B15 !important;
  color: #FFFFFF !important;
  font-weight: 600 !important;
}

/* Style Streamlit tabs as clean pill rows (ink pill with white text for active) */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 10px !important;
  background-color: transparent !important;
  border-bottom: none !important;
  padding: 4px 0 16px 0 !important;
  overflow-x: auto !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
  border-radius: 999px !important;
  border: 1px solid var(--line) !important;
  background-color: #FFFFFF !important;
  color: var(--muted) !important;
  height: 38px !important;
  min-height: 38px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  padding: 0 18px !important;
  transition: all 0.15s ease !important;
  white-space: nowrap !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"]:hover {
  border-color: #CBD0C5 !important;
  color: var(--ink) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
  background-color: #0F1B15 !important;
  border: 1px solid #0F1B15 !important;
  color: #FFFFFF !important;
  font-weight: 600 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
div[data-testid="stTabs"] [data-baseweb="tab-border"] {
  display: none !important;
}

/* Page Intro block */
.page-intro-block {
  max-width: 1040px;
  margin: 0 auto 28px;
}
.page-intro-eyebrow {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--good);
  margin-bottom: 6px;
}
.page-intro-title {
  font-family: 'Space Grotesk', 'Mukta', sans-serif;
  font-size: 40px;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.15;
  margin: 0 0 8px 0;
}
.page-intro-subtitle {
  font-size: 16px;
  color: #4A554F;
  line-height: 1.5;
  margin: 0;
}

div[data-testid="stVerticalBlock"]:has(> div > [data-testid="stVerticalBlockBorderWrapper"].wizard-card-anchor),
div:has(> .wizard-card-anchor) {
  max-width: 760px !important;
  margin-left: auto !important;
  margin-right: auto !important;
}

.wizard-card-title {
  font-family: 'Space Grotesk', 'Mukta', sans-serif !important;
  font-size: 28px !important;
  font-weight: 700 !important;
  color: var(--ink) !important;
  line-height: 1.25 !important;
  margin: 0 0 6px 0 !important;
}
.wizard-card-hint {
  font-size: 15px !important;
  color: var(--muted) !important;
  line-height: 1.5 !important;
  margin: 0 0 20px 0 !important;
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
}
/* Where you stand hero card */
.where-you-stand-card {
  background: #FFFFFF !important;
  border: 1px solid var(--line) !important;
  border-radius: 20px !important;
  padding: 28px !important;
  margin-bottom: 24px !important;
  box-shadow: 0 4px 20px rgba(15,27,21,0.04) !important;
}
.where-you-stand-card.good {
  border-left: 6px solid #1F7A4D !important;
}
.where-you-stand-card.almost {
  border-left: 6px solid #B7791F !important;
}
.where-you-stand-card.work {
  border-left: 6px solid #B5523B !important;
}

.eyebrow-label {
  font-size: 12px !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
  color: var(--muted) !important;
  margin-bottom: 6px !important;
}

.where-you-stand-title {
  font-family: 'Space Grotesk', 'Mukta', sans-serif !important;
  font-size: 40px !important;
  font-weight: 700 !important;
  color: var(--ink) !important;
  line-height: 1.15 !important;
  margin: 0 0 16px 0 !important;
}

/* Stat cards in a row */
.stat-box-card {
  background: #FFFFFF !important;
  border: 1px solid var(--line) !important;
  border-radius: 20px !important;
  padding: 20px !important;
  height: 100% !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: space-between !important;
}

.stat-box-num {
  font-family: 'Space Grotesk', 'Mukta', sans-serif !important;
  font-size: 28px !important;
  font-weight: 700 !important;
  line-height: 1.2 !important;
  margin: 4px 0 6px 0 !important;
}

/* Compare offer card top accents */
.offer-card-a {
  border-top: 4px solid var(--good) !important;
}
.offer-card-b {
  border-top: 4px solid var(--ink) !important;
}
.offer-card-c {
  border-top: 4px solid var(--warn) !important;
}

/* Compare clean table */
.compare-clean-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--line);
  margin: 16px 0;
  background: #FFFFFF;
}
.compare-clean-table th,
.compare-clean-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--line);
  font-size: 14px;
}
.compare-clean-table th {
  background: #F8F9F6;
  font-family: 'Space Grotesk', 'Mukta', sans-serif;
  font-weight: 700;
  color: var(--ink);
  text-align: right;
}
.compare-clean-table th:first-child {
  text-align: left;
}
.compare-clean-table td {
  text-align: right;
  font-family: 'Space Grotesk', 'Inter', monospace;
  color: var(--ink);
}
.compare-clean-table td:first-child {
  text-align: left;
  font-family: 'Inter', 'Mukta', sans-serif;
  font-weight: 600;
  color: var(--muted);
}
.compare-clean-table tr:last-child td {
  border-bottom: none;
}
.compare-clean-table .highlight-col {
  background-color: #F1F9DF !important;
}

/* Safety question row */
.safety-q-card {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 10px;
}

/* Numbered step circle (lime) */
.num-circle-lime {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--accent);
  color: var(--ink);
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  display: inline-grid;
  place-items: center;
  font-size: 14px;
  line-height: 1;
  flex-shrink: 0;
}

/* CIBIL scale bar */
.cibil-scale-bar {
  display: flex;
  height: 12px;
  border-radius: 999px;
  overflow: hidden;
  margin: 12px 0 8px;
  width: 100%;
}
.cibil-scale-segment {
  height: 100%;
}
.next-step-banner {
  background: #0F1B15 !important;
  color: #FFFFFF !important;
  border-radius: 20px !important;
  padding: 24px 28px !important;
  margin: 28px 0 !important;
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  flex-wrap: wrap !important;
  gap: 16px !important;
}

/* Lender row */
.lender-row-item {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 14px 18px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  transition: border-color 0.15s ease;
}
.lender-row-item:hover {
  border-color: #CBD0C5;
}

/* Number input clean label */
.clean-num-input div[data-testid="stWidgetLabel"] label p {
  font-size: 14px !important;
  font-weight: 600 !important;
  color: var(--ink) !important;
}

/* Cards & Containers */
div[data-testid="stVerticalBlockBorderWrapper"][style*="border"], .feature-card, .step-card, .panel, .result-card, .case-card {
  background: #FFFFFF !important;
  border: 1px solid #E2E5DC !important;
  border-radius: 20px !important;
  padding: 24px 28px !important;
}
a.card {
  transition: transform .15s, box-shadow .15s;
}
a.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 30px -18px rgba(15,27,21,.4);
}

/* Progress bars */
div[data-testid="stProgress"] > div {
  background-color: #E9ECE4 !important;
  border-radius: 999px !important;
  overflow: hidden !important;
}
div[data-testid="stProgress"] > div > div {
  background-color: var(--good) !important;
  border-radius: 999px !important;
}
div[data-testid="stProgress"] > div > div > div {
  background-color: var(--good) !important;
}

/* Sliders */
.stSlider [data-testid="stSliderThumbValue"],.stSlider [data-testid="stSliderTickBarMin"],.stSlider [data-testid="stSliderTickBarMax"]{display:none!important}
.stSlider:has([aria-label*="Repayment"]) [data-testid="stSliderTickBarMin"],.stSlider:has([aria-label*="Repayment"]) [data-testid="stSliderTickBarMax"],.stSlider:has([aria-label*="Repayment"]) [data-testid="stSliderThumbValue"],.stSlider:has([aria-label*="अवधि"]) [data-testid="stSliderTickBarMin"],.stSlider:has([aria-label*="अवधि"]) [data-testid="stSliderTickBarMax"],.stSlider:has([aria-label*="अवधि"]) [data-testid="stSliderThumbValue"],.stSlider:has([aria-valuetext*="month"]) [data-testid="stSliderTickBarMin"],.stSlider:has([aria-valuetext*="month"]) [data-testid="stSliderTickBarMax"],.stSlider:has([aria-valuetext*="month"]) [data-testid="stSliderThumbValue"],.stSlider:has([aria-valuetext*="महीने"]) [data-testid="stSliderTickBarMin"],.stSlider:has([aria-valuetext*="महीने"]) [data-testid="stSliderTickBarMax"],.stSlider:has([aria-valuetext*="महीने"]) [data-testid="stSliderThumbValue"]{display:block!important}

/* Responsive */
@media (max-width: 640px) {
  div[data-testid="stHorizontalBlock"]:has(.hdr-nav) {
    flex-wrap: wrap !important;
    padding: 16px 20px !important;
    gap: 12px 0 !important;
  }
  div[data-testid="stHorizontalBlock"]:has(.hdr-nav) > div[data-testid="column"]:nth-child(1) {
    order: 1 !important;
    width: 50% !important;
    flex: 0 0 50% !important;
  }
  div[data-testid="stHorizontalBlock"]:has(.hdr-nav) > div[data-testid="column"]:nth-child(3) {
    order: 2 !important;
    width: 50% !important;
    flex: 0 0 50% !important;
  }
  div[data-testid="stHorizontalBlock"]:has(.hdr-nav) > div[data-testid="column"]:nth-child(2) {
    order: 3 !important;
    width: 100% !important;
    flex: 0 0 100% !important;
    margin-top: 8px !important;
  }
  .hdr-nav {
    justify-content: flex-start !important;
    gap: 20px !important;
    overflow-x: auto !important;
    padding-bottom: 4px !important;
    -webkit-overflow-scrolling: touch;
  }
}

div[data-testid="stVerticalBlockBorderWrapper"]:not(.st-emotion-cache-0){background:#FFFFFF !important;border:1px solid #E2E5DC !important;border-radius:20px !important;padding:24px 28px !important;}
div[data-testid="stHorizontalBlock"]:has(.hdr-nav){width:100% !important;}
div[data-testid="stHorizontalBlock"]:has(.hdr-nav) > div{min-width:0 !important;}
div[data-testid="stHorizontalBlock"]:has(.hdr-nav) *{white-space:nowrap !important;}

button[data-testid="stBaseButton-pills"], button[data-testid="stBaseButton-pillsActive"]{height:38px !important;min-height:38px !important;padding:0 16px !important;border-radius:999px !important;display:inline-flex !important;align-items:center !important;justify-content:center !important;background:#FFFFFF !important;border:1px solid #E2E5DC !important;box-shadow:none !important;color:#0F1B15 !important;}
button[data-testid="stBaseButton-pills"]:hover{border-color:#B9C0B5 !important;background:#FAFBF7 !important;}
button[data-testid="stBaseButton-pillsActive"]{background:#F1F9DF !important;border:2px solid #0F1B15 !important;font-weight:600 !important;}
button[data-testid="stBaseButton-pills"] p, button[data-testid="stBaseButton-pillsActive"] p, button[data-testid="stBaseButton-pills"] [data-testid="stMarkdownContainer"], button[data-testid="stBaseButton-pillsActive"] [data-testid="stMarkdownContainer"]{margin:0 !important;padding:0 !important;line-height:1 !important;font-size:14px !important;color:#0F1B15 !important;text-decoration:none !important;display:flex !important;align-items:center !important;}
button[data-testid="stBaseButton-pillsActive"] p{font-weight:600 !important;}
button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primary"] p{color:#0F1B15 !important;}
</style>"""

def page_setup():
    try:
        st.set_page_config(page_title="Kreditly · Loan readiness",page_icon="🟩",layout="wide",initial_sidebar_state="collapsed")
    except Exception:
        pass
    st.markdown(CSS,unsafe_allow_html=True)

def _toggle_language():
    """Switch between English and Hindi before page text is rendered."""
    st.session_state.language = "हिं" if st.session_state.get("language", "EN") == "EN" else "EN"

def header(active=""):
    if "language" not in st.session_state:
        st.session_state.language = "EN"
    cur_lang = st.session_state.language

    col_logo, col_nav, col_lang = st.columns([2.2, 6.0, 1.6], vertical_alignment="center", gap="small")

    with col_logo:
        st.markdown(
            '<a href="/" target="_self" style="display: flex; align-items: center; gap: 10px; text-decoration: none; color: #0F1B15; white-space: nowrap;">'
            '<span style="width: 34px; height: 34px; border-radius: 10px; background: #0F1B15; display: grid; place-items: center; color: #C6F24E; font-family: \'Space Grotesk\', sans-serif; font-size: 20px; font-weight: 700; line-height: 1; flex-shrink: 0;">k</span>'
            '<span class="sg" style="font-size: 20px; font-weight: 700; letter-spacing: -0.02em; white-space: nowrap;">kreditly</span>'
            '</a>',
            unsafe_allow_html=True,
        )

    with col_nav:
        def _act(k): return 'class="active"' if active == k else ''
        st.markdown(
            f'<nav class="hdr-nav">'
            f'<a href="/Check_Eligibility" target="_self" {_act("check")}>{t("nav_check")}</a>'
            f'<a href="/Tools" target="_self" {_act("tools")}>{t("nav_tools")}</a>'
            f'<a href="/Guide" target="_self" {_act("guide")}>{t("nav_guide")}</a>'
            f'<a href="/Sample_Cases" target="_self" {_act("samples")}>{t("nav_samples")}</a>'
            f'</nav>',
            unsafe_allow_html=True,
        )

    with col_lang:
        cls_lang = "lang-en" if cur_lang == "EN" else "lang-hi"
        st.markdown(f'<div class="hdr-lang-wrap {cls_lang}">', unsafe_allow_html=True)
        btn_label = "**EN** · हिं" if cur_lang == "EN" else "EN · **हिं**"
        if st.button(btn_label, key="toggle_language", on_click=_toggle_language):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def render_wizard_step_bar(current_step: int, total_steps: int = 5):
    """Render the 5 step names with checkmarks for completed, bold ink for current, muted for future, plus thin progress line."""
    step_keys = ["step_loan", "step_income", "step_emis", "step_credit", "step_about"]
    names = [t(k) for k in step_keys]
    
    items_html = []
    for idx, name in enumerate(names, start=1):
        if idx < current_step:
            cls = "step-done"
            label = f'<span style="color:#1F7A4D;font-weight:700;margin-right:3px;">✓</span> {name}'
        elif idx == current_step:
            cls = "step-current"
            label = f'<strong style="color:#0F1B15;font-weight:700;">{name}</strong>'
        else:
            cls = "step-future"
            label = f'<span style="color:#4A554F;font-weight:500;">{name}</span>'
        items_html.append(f'<span class="wizard-step-item {cls}">{label}</span>')

    pct = int(round((current_step / total_steps) * 100))
    steps_joined = " · ".join(items_html)

    st.markdown(
        f'<div class="wizard-step-header" style="margin-bottom:24px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;font-size:13px;margin-bottom:10px;">'
        f'{steps_joined}'
        f'</div>'
        f'<div style="height:4px;background:#E9ECE4;border-radius:999px;overflow:hidden;width:100%;">'
        f'<div style="height:100%;width:{pct}%;background:#C6F24E;border-radius:999px;transition:width 0.3s ease;"></div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

def card(key: str | None = None):
    """Return a styled white container matching the design tokens."""
    return st.container(border=True)

def chip_selector(label: str, options: list[str], default_value: str, key: str) -> str:
    """Render modern tap-to-answer chips with fallback across Streamlit versions."""
    is_testing = "$$STREAMLIT_INTERNAL_KEY_TESTING" in st.session_state
    if not is_testing and hasattr(st, "pills"):
        val = st.pills(label, options, default=default_value, key=key)
        return val if val is not None else default_value
    elif not is_testing and hasattr(st, "segmented_control"):
        val = st.segmented_control(label, options, default=default_value, key=key)
        return val if val is not None else default_value
    else:
        idx = options.index(default_value) if default_value in options else 0
        return st.radio(label, options, index=idx, horizontal=True, key=key)

def render_running_emi(loan_amount: float, rate: float, tenure_months: int):
    """Render a compact running EMI estimate from screen 1 onward."""
    s = loan_summary(loan_amount, rate, tenure_months)
    st.markdown(
        f'<div style="background:#F1F9DF;border:1px solid #D5E8B1;border-radius:12px;padding:12px 16px;margin:8px 0 20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">'
        f'<span style="font-size:13px;color:#35443A;font-weight:600;">{t("running_emi_hint", amount=format_inr(s["emi"]))}</span>'
        f'<span style="font-size:12px;color:#52751E;">{tenure_months} {t("months")} @ {rate:.1f}%</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
def footer():
    st.markdown(
        f'<footer class="kd-footer" style="border-top: 1px solid #E2E5DC; max-width: 1200px; margin: 48px auto 0; padding: 24px 32px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; font-size: 13px; color: #4A554F; background: transparent !important;">'
        f'<div>{t("footer_built_by")}</div>'
        f'<div style="display: flex; gap: 16px;">'
        f'<a href="/Model_Insights" target="_self" style="color: #4A554F; text-decoration: underline; text-underline-offset: 2px;">{t("footer_how_models_work")}</a>'
        f'<a href="/About" target="_self" style="color: #4A554F; text-decoration: underline; text-underline-offset: 2px;">{t("footer_about_privacy")}</a>'
        f'</div>'
        f'</footer>',
        unsafe_allow_html=True,
    )

def render_feedback(key: str):
    """Render a lightweight 'Was this helpful?' feedback widget with no tracking."""
    st.markdown('<div style="margin-top:24px;padding-top:14px;border-top:1px solid var(--line);"></div>', unsafe_allow_html=True)
    feedback_key = f"fb_{key}"
    answered_key = f"fb_answered_{key}"

    if st.session_state.get(answered_key):
        st.markdown(
            f'<div style="font-size:13px;color:#1F7A4D;padding:6px 0;">'
            f'✅ {t("feedback_thanks")} <a href="https://github.com/revaank/kreditly/issues/new" target="_blank" rel="noopener noreferrer" style="color:#1F7A4D;text-decoration:underline;font-weight:600;">GitHub Issues ↗</a>'
            f'</div>',
            unsafe_allow_html=True,
        )
        return

    col_q, col_w = st.columns([2.5, 4.5], vertical_alignment="center")
    with col_q:
        st.markdown(f'<span style="font-size:14px;color:#4A554F;font-weight:600;">{t("feedback_helpful_q")}</span>', unsafe_allow_html=True)
    with col_w:
        is_testing = "$$STREAMLIT_INTERNAL_KEY_TESTING" in st.session_state
        if not is_testing and hasattr(st, "feedback"):
            val = st.feedback("thumbs", key=feedback_key)
            if val is not None:
                st.session_state[answered_key] = True
                st.rerun()
        else:
            b1, b2, _ = st.columns([1, 1, 8])
            with b1:
                if st.button("👍", key=f"btn_up_{key}"):
                    st.session_state[answered_key] = True
                    st.rerun()
            with b2:
                if st.button("👎", key=f"btn_down_{key}"):
                    st.session_state[answered_key] = True
                    st.rerun()
def page_intro(eyebrow: str, title: str, subtitle: str | None = None):
    """Render a common page intro block with green eyebrow, 40px Space Grotesk title, and 16px muted subtitle."""
    sub_html = f'<div class="page-intro-subtitle">{subtitle}</div>' if subtitle else ''
    st.markdown(
        f'<div class="page-intro-block">'
        f'<div class="page-intro-eyebrow">{eyebrow}</div>'
        f'<h1 class="page-intro-title">{title}</h1>'
        f'{sub_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

def section_title(title,subtitle=None):
    st.markdown(f"## {title}")
    if subtitle: st.caption(subtitle)

def money_input(label,key,value,step=1000):
    """Text input that keeps rupee values readable with Indian digit grouping."""
    displayed=format_inr(value).replace("₹","")
    raw=st.text_input(f"{label} (₹)",value=displayed,key=f"money_{key}")
    cleaned=raw.replace("₹","").replace(",","").replace(" ","")
    try:
        amount=float(cleaned) if cleaned else 0.0
        if amount < 0: raise ValueError
        return int(amount),True
    except ValueError:
        st.caption(t("money_input_hint"))
        return int(value),False

def contribution_chart(contributions,height=330):
    """Render the same color-coded explanation chart on results and examples."""
    labels=[t("feature_"+item["feature"]) for item in contributions]
    colors=["#F87171" if item["contribution"]>0 else "#34D399" for item in contributions]
    figure=go.Figure(go.Bar(x=[item["contribution"] for item in contributions],y=labels,orientation="h",marker_color=colors))
    figure.update_layout(height=height,margin=dict(l=10,r=10,t=12,b=20),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",xaxis_title=t("contribution_axis"),yaxis=dict(autorange="reversed"))
    st.plotly_chart(figure,use_container_width=True)

def format_risk_pct(risk: float) -> str:
    """Format risk probability into a percentage string, never displaying 0%."""
    try:
        val = float(risk)
    except (TypeError, ValueError):
        val = 0.0
    if val < 0.01:
        return t("risk_under_one")
    return f"{round(val * 100)}%"

def result_card(result, show_risk_details=True):
    band=result.get("readiness_band","fair")
    tone={"good":"strong","fair":"borderline","needs_work":"risky"}.get(band,"borderline")
    risk_val = float(result.get("risk", 0.0))
    risk_display = format_risk_pct(risk_val)
    meter_pct = max(6, min(100, round(risk_val * 100))) if risk_val > 0 else 6
    title=t(f"readiness_{band}")
    st.markdown(f'<div class="result-card {tone}"><div class="small-label">{t("readiness_band")}</div><div class="risk-number" style="font-size:34px">{title}</div><div class="muted">{t("dummy_notice")}</div><div style="height:14px"></div><div class="risk-track"><div class="risk-fill {tone}" style="width:{meter_pct}%"></div></div></div>',unsafe_allow_html=True)
    if show_risk_details:
        with st.expander(t("risk_details")):
            st.metric(t("calibrated_risk"), risk_display)
    else:
        st.caption(f'{t("risk_details")}: {t("calibrated_risk")} {risk_display}')

def format_whatif_delta(delta: float) -> str:
    """Format the change in risk points into localized text."""
    pts = round(abs(delta) * 100)
    if pts == 0:
        return t("no_change")
    if delta < 0:
        label = t("point_lower", points=pts) if pts == 1 else t("points_lower", points=pts)
        return f"↓ {label}"
    label = t("point_higher", points=pts) if pts == 1 else t("points_higher", points=pts)
    return f"↑ {label}"

def render_whatif_result(result, original, show_risk_details=True):
    """Show a calibrated readiness band and a neutral/colored risk delta."""
    band = t(f"readiness_{result.get('readiness_band', 'fair')}")
    delta = float(result["risk"]) - float(original["risk"])
    pts = round(abs(delta) * 100)
    if pts == 0:
        delta_html = f'<span class="delta-neutral">{t("no_change")}</span>'
    elif delta < 0:
        label = t("point_lower", points=pts) if pts == 1 else t("points_lower", points=pts)
        delta_html = f'<span class="delta-down">↓ {label}</span>'
    else:
        label = t("point_higher", points=pts) if pts == 1 else t("points_higher", points=pts)
        delta_html = f'<span class="delta-up">↑ {label}</span>'
    st.markdown(
        f'<div class="whatif-result"><div class="small-label">{t("simulator_result")}</div>'
        f'<strong>{band}</strong><div>{delta_html}</div></div>', unsafe_allow_html=True,
    )
    detail = f'{t("calibrated_risk")}: {format_risk_pct(result["risk"])} · {t("original_risk")}: {format_risk_pct(original["risk"])}'
    if show_risk_details:
        with st.expander(t("risk_details")):
            st.caption(detail)
    else:
        st.caption(f'{t("risk_details")}: {detail}')

def render_emi_planner(principal: float, rate: float, selected_months: int):
    """Render a 12/24/36/48/60 month EMI and total interest comparison grid."""
    section_title(t("v2_feature4"), t("v2_feature4_body"))
    terms = [12, 24, 36, 48, 60]
    cols = st.columns(len(terms))
    for term, col in zip(terms, cols):
        s = loan_summary(principal, rate, term)
        is_selected = (int(term) == int(selected_months))
        highlight_style = 'border: 2px solid #0F1B15; background: #F1F9DF;' if is_selected else 'border: 1px solid #E2E5DC; background: #FFFFFF;'
        badge = f'<span style="background:#0F1B15;color:#C6F24E;border-radius:999px;padding:3px 8px;font-size:11px;font-weight:700;">{t("selected_term")}</span>' if is_selected else ''
        with col:
            col.markdown(
                f'<div style="{highlight_style} border-radius: 14px; padding: 14px; text-align: center; height: 100%;">'
                f'<div style="min-height: 22px; margin-bottom: 4px;">{badge}</div>'
                f'<div style="font-size: 15px; font-weight: 700; color: #0F1B15; margin-bottom: 8px;">{term} {t("months")}</div>'
                f'<div style="font-size: 18px; font-weight: 700; color: #0F1B15; font-family: Sora, sans-serif;">{format_inr(s["emi"])}</div>'
                f'<div style="font-size: 11px; color: #4A554F; margin-bottom: 10px;">{t("per_month")}</div>'
                f'<div style="border-top: 1px solid #E2E5DC; padding-top: 8px; font-size: 11px; color: #4A554F;">{t("total_interest")}:<br><b>{format_inr(s["interest"])}</b></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

def build_download_report(result: dict, summary: dict, ratio: float, bank_results=None) -> str:
    """Build the plain text report containing readiness band, lender results, and disclaimer."""
    from .bank_checker import count_meets, load_bank_rules
    band_name = t(f"readiness_{result.get('readiness_band', 'fair')}")
    label_key = {"STRONG": "strong", "BORDERLINE": "borderline", "RISKY": "risky"}.get(
        result.get("label", "BORDERLINE"), "borderline"
    )
    report_lines = [
        t("report"),
        t("report_dummy"),
        t("readiness_result", band=band_name),
        f'{t("risk_details")}: {t("calibrated_risk")} {format_risk_pct(result.get("risk", 0.0))} ({t(label_key)})',
        f'{t("monthly_emi")}: {format_inr(summary.get("emi", 0.0))}',
        f'{t("salary_emi")}: {ratio:.1f}%',
    ]
    if bank_results is not None:
        report_lines.append(t("bank_summary", count=count_meets(bank_results), total=len(bank_results)))
        for item in bank_results:
            st_key = "qualify_badge_limited" if item["status"] == "limited" else f"bank_status_{item['status']}"
            report_lines.append(f'{item["name"]}: {t(st_key)}')
    try:
        bank_metadata = load_bank_rules()
        report_lines.extend([
            t("bank_last_checked", date=bank_metadata.get("last_checked", "")),
            t("bank_disclaimer"),
        ])
    except Exception:
        report_lines.append(t("bank_disclaimer"))
    report_lines.append(t("report_no_personal"))
    return "\n".join(report_lines)
