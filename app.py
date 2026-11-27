"""Kreditly home page: loan readiness preparation for first-time borrowers in India."""
from __future__ import annotations

from datetime import datetime
import streamlit as st

from src.bank_checker import load_bank_rules
from src.translations import t
from src.ui import footer, header, page_setup

page_setup()
header("home")

# Custom styles for landing page components
st.markdown("""
<style>
.hero-eyebrow {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #1F7A4D;
  margin-bottom: 16px;
}
.hero-title {
  font-family: 'Space Grotesk', 'Mukta', sans-serif !important;
  font-size: clamp(36px, 4.2vw, 54px) !important;
  font-weight: 700 !important;
  line-height: 1.08 !important;
  letter-spacing: -0.04em !important;
  color: var(--ink) !important;
  margin: 0 0 18px 0;
}
.hero-sub {
  font-size: 18px;
  line-height: 1.6;
  color: var(--muted);
  max-width: 520px;
  margin: 0 0 28px 0;
}
.hero-actions {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 22px;
}
.hero-example-link {
  font-size: 15px;
  font-weight: 600;
  color: var(--ink);
  text-decoration: underline;
  text-underline-offset: 3px;
}
.hero-example-link:hover {
  color: var(--good);
}
.hero-trust {
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
}

/* Preview Card */
.preview-card {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 20px;
  padding: 26px 28px;
  box-shadow: 0 24px 60px -30px rgba(15,27,21,.35);
}
.preview-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.preview-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}
.preview-badge {
  font-size: 11px;
  font-weight: 700;
  background: #ECFCCB;
  color: #365314;
  padding: 3px 9px;
  border-radius: 999px;
}
.preview-status {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.preview-check-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--good);
  color: #FFFFFF;
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 16px;
  flex-shrink: 0;
}
.preview-status-text {
  font-family: 'Space Grotesk', 'Mukta', sans-serif;
  font-size: 24px;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.2;
}
.preview-panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 20px;
}
.preview-panel {
  background: var(--soft);
  border-radius: 14px;
  padding: 12px 14px;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--good);
  line-height: 1.35;
}
.preview-foir {
  margin-bottom: 20px;
}
.preview-foir-header {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 7px;
}
.preview-foir-bar {
  height: 6px;
  border-radius: 999px;
  background: #E9ECE4;
  overflow: hidden;
  margin-bottom: 6px;
}
.preview-foir-fill {
  height: 100%;
  border-radius: 999px;
  background: var(--good);
}
.preview-foir-caption {
  font-size: 11.5px;
  color: var(--muted);
}
.preview-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.chip-bank {
  font-size: 12px;
  font-weight: 600;
  color: #365314;
  background: #ECFCCB;
  padding: 4px 10px;
  border-radius: 999px;
}
.chip-nbfc {
  font-size: 12px;
  font-weight: 600;
  color: #854D0E;
  background: #FEF3C7;
  padding: 4px 10px;
  border-radius: 999px;
}
.chip-more {
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
  padding: 4px 6px;
}

/* 4 Tiles */
.section-title-wrap {
  margin-top: 64px;
  margin-bottom: 24px;
}
.section-title {
  font-family: 'Space Grotesk', 'Mukta', sans-serif;
  font-size: 26px;
  font-weight: 700;
  color: var(--ink);
  margin: 0;
}
.tools-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}
.tool-tile {
  border-radius: 20px;
  padding: 24px;
  text-decoration: none !important;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 220px;
  transition: all 0.2s ease;
}
.tool-tile.standard {
  background: #FFFFFF;
  border: 1px solid var(--line);
  box-shadow: 0 4px 16px rgba(15,27,21,0.025);
}
.tool-tile.standard:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(15,27,21,0.07);
}
.tool-tile.dark {
  background: var(--ink);
  border: 1px solid var(--ink);
  box-shadow: 0 6px 20px rgba(15,27,21,0.12);
}
.tool-tile.dark:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 34px rgba(15,27,21,0.18);
}
.tile-icon-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--accent);
  display: grid;
  place-items: center;
  flex-shrink: 0;
  margin-bottom: 18px;
}
.tile-title {
  font-family: 'Space Grotesk', 'Mukta', sans-serif;
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 8px 0;
}
.tool-tile.standard .tile-title { color: var(--ink); }
.tool-tile.dark .tile-title { color: #FFFFFF; }
.tile-desc {
  font-size: 13.5px;
  line-height: 1.5;
  margin: 0 0 18px 0;
  flex-grow: 1;
}
.tool-tile.standard .tile-desc { color: var(--muted); }
.tool-tile.dark .tile-desc { color: #C3CEC6; }
.tile-action {
  font-size: 14px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 4px;
}
.tool-tile.standard .tile-action { color: var(--ink); }
.tool-tile.dark .tile-action { color: var(--accent); }
@media (max-width: 900px) {
  .tools-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 600px) {
  .tools-grid { grid-template-columns: 1fr; }
}

/* How It Works Band */
.how-band {
  background: rgba(238,240,234,.75);
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  border-radius: 20px;
  padding: 56px 36px;
  margin-top: 64px;
}
.how-heading {
  font-family: 'Space Grotesk', 'Mukta', sans-serif;
  font-size: 26px;
  font-weight: 700;
  color: var(--ink);
  margin: 0 0 42px 0;
  text-align: center;
}
.steps-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 36px;
  position: relative;
}
.step-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.step-circle {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--accent);
  color: var(--ink);
  font-family: 'Space Grotesk', sans-serif;
  font-size: 20px;
  font-weight: 700;
  display: grid;
  place-items: center;
  margin-bottom: 18px;
  position: relative;
  z-index: 2;
}
.step-line {
  position: absolute;
  top: 26px;
  left: 52px;
  right: -36px;
  height: 2px;
  background: #D7DCCF;
  z-index: 1;
}
.step-item:last-child .step-line {
  display: none;
}
.step-title {
  font-family: 'Space Grotesk', 'Mukta', sans-serif;
  font-size: 18px;
  font-weight: 700;
  color: var(--ink);
  margin: 0 0 8px 0;
}
.step-desc {
  font-size: 14px;
  line-height: 1.6;
  color: var(--muted);
  margin: 0;
}
@media (max-width: 768px) {
  .steps-row { grid-template-columns: 1fr; gap: 28px; }
  .step-line { display: none; }
}

/* Lenders Section */
.lenders-card {
  background: #FFFFFF;
  border: 1px solid var(--line);
  border-radius: 20px;
  padding: 32px;
  margin-top: 64px;
}
.lenders-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 24px;
}
.lenders-title {
  font-family: 'Space Grotesk', 'Mukta', sans-serif;
  font-size: 20px;
  font-weight: 700;
  color: var(--ink);
  margin: 0;
}
.lenders-meta {
  font-size: 13.5px;
  color: var(--muted);
}
.lenders-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px 18px;
  padding: 18px 0;
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
}
.lender-item {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 15px;
  font-weight: 600;
  color: var(--ink);
}
.lender-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}
.lender-dot.bank { background: #1F7A4D; }
.lender-dot.nbfc { background: #7A9A12; }
.lenders-legend {
  margin-top: 16px;
  font-size: 12px;
  display: flex;
  gap: 16px;
}
.leg-bank { color: #1F7A4D; font-weight: 600; }
.leg-nbfc { color: #7A9A12; font-weight: 600; }
@media (max-width: 800px) {
  .lenders-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 500px) {
  .lenders-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# TASK 2.A — Hero Section
# ==============================================================================
col_hero_left, col_hero_right = st.columns([1.1, 0.9], gap="large", vertical_alignment="center")

with col_hero_left:
    st.markdown(f'<div class="hero-eyebrow">{t("eyebrow_home")}</div>', unsafe_allow_html=True)
    st.markdown(f'<h1 class="hero-title">{t("v2_title")}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="hero-sub">{t("hero_subtext")}</p>', unsafe_allow_html=True)

    c_btn, c_link = st.columns([1.4, 1.0], vertical_alignment="center")
    with c_btn:
        with st.container(key="hero_cta"):
            if st.button(t("hero_cta"), use_container_width=True):
                st.switch_page("pages/1_Check_Eligibility.py")
    with c_link:
        st.markdown(f'<a href="/Sample_Cases" target="_self" class="hero-example-link">{t("hero_example_link")} →</a>', unsafe_allow_html=True)

    st.markdown(f'<div class="hero-trust">{t("hero_trust")}</div>', unsafe_allow_html=True)

with col_hero_right:
    st.markdown(
        f'<div class="preview-card">'
        f'  <div class="preview-top">'
        f'    <span class="preview-label">{t("preview_your_result")}</span>'
        f'    <span class="preview-badge">{t("preview_example_tag")}</span>'
        f'  </div>'
        f'  <div class="preview-status">'
        f'    <div class="preview-check-circle">✓</div>'
        f'    <div class="preview-status-text">{t("preview_good_position")}</div>'
        f'  </div>'
        f'  <div class="preview-panels">'
        f'    <div class="preview-panel">{t("preview_safely_borrow")}</div>'
        f'    <div class="preview-panel">{t("preview_lenders_matched")}</div>'
        f'  </div>'
        f'  <div class="preview-foir">'
        f'    <div class="preview-foir-header">{t("preview_salary_emi")}</div>'
        f'    <div class="preview-foir-bar">'
        f'      <div class="preview-foir-fill" style="width: 23%;"></div>'
        f'    </div>'
        f'    <div class="preview-foir-caption">{t("preview_foir_caption")}</div>'
        f'  </div>'
        f'  <div class="preview-chips">'
        f'    <span class="chip-bank">● SBI</span>'
        f'    <span class="chip-bank">● HDFC</span>'
        f'    <span class="chip-bank">● ICICI</span>'
        f'    <span class="chip-nbfc">● IndusInd</span>'
        f'    <span class="chip-more">{t("preview_more_lenders")}</span>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# ==============================================================================
# TASK 2.B — "What you can do here" (4 tiles)
# ==============================================================================
icon_target = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0F1B15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>'
icon_scales = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0F1B15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>'
icon_shield = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0F1B15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>'
icon_rotate = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0F1B15" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>'

st.markdown(
    f'<div class="section-title-wrap">'
    f'  <h2 class="section-title">{t("what_you_can_do")}</h2>'
    f'</div>'
    f'<div class="tools-grid">'
    f'  <a href="/Check_Eligibility" target="_self" class="tool-tile dark">'
    f'    <div>'
    f'      <div class="tile-icon-circle">{icon_target}</div>'
    f'      <h3 class="tile-title">{t("tile1_title")}</h3>'
    f'      <p class="tile-desc">{t("tile1_desc")}</p>'
    f'    </div>'
    f'    <div class="tile-action">{t("tile1_action")}</div>'
    f'  </a>'
    f'  <a href="/Tools?tab=compare" target="_self" class="tool-tile standard">'
    f'    <div>'
    f'      <div class="tile-icon-circle">{icon_scales}</div>'
    f'      <h3 class="tile-title">{t("tile2_title")}</h3>'
    f'      <p class="tile-desc">{t("tile2_desc")}</p>'
    f'    </div>'
    f'    <div class="tile-action">{t("tile2_action")}</div>'
    f'  </a>'
    f'  <a href="/Tools?tab=safety" target="_self" class="tool-tile standard">'
    f'    <div>'
    f'      <div class="tile-icon-circle">{icon_shield}</div>'
    f'      <h3 class="tile-title">{t("tile3_title")}</h3>'
    f'      <p class="tile-desc">{t("tile3_desc")}</p>'
    f'    </div>'
    f'    <div class="tile-action">{t("tile3_action")}</div>'
    f'  </a>'
    f'  <a href="/Tools?tab=rejected" target="_self" class="tool-tile standard">'
    f'    <div>'
    f'      <div class="tile-icon-circle">{icon_rotate}</div>'
    f'      <h3 class="tile-title">{t("tile4_title")}</h3>'
    f'      <p class="tile-desc">{t("tile4_desc")}</p>'
    f'    </div>'
    f'    <div class="tile-action">{t("tile4_action")}</div>'
    f'  </a>'
    f'</div>',
    unsafe_allow_html=True,
)

# ==============================================================================
# TASK 2.C — "How it works" Band
# ==============================================================================
st.markdown(
    f'<div class="how-band">'
    f'  <h2 class="how-heading">{t("how_title")}</h2>'
    f'  <div class="steps-row">'
    f'    <div class="step-item">'
    f'      <div class="step-circle">1</div>'
    f'      <div class="step-line"></div>'
    f'      <h3 class="step-title">{t("step1")}</h3>'
    f'      <p class="step-desc">{t("step1_body")}</p>'
    f'    </div>'
    f'    <div class="step-item">'
    f'      <div class="step-circle">2</div>'
    f'      <div class="step-line"></div>'
    f'      <h3 class="step-title">{t("step2")}</h3>'
    f'      <p class="step-desc">{t("step2_body")}</p>'
    f'    </div>'
    f'    <div class="step-item">'
    f'      <div class="step-circle">3</div>'
    f'      <h3 class="step-title">{t("step3")}</h3>'
    f'      <p class="step-desc">{t("step3_body")}</p>'
    f'    </div>'
    f'  </div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ==============================================================================
# TASK 2.D — 15 Lenders Section
# ==============================================================================
try:
    bank_data = load_bank_rules()
    lenders_list = bank_data.get("lenders", [])
    raw_date = bank_data.get("last_checked", "2026-11-27")
    try:
        dt = datetime.strptime(raw_date, "%Y-%m-%d")
        formatted_date = dt.strftime("%d %b %Y")
    except Exception:
        formatted_date = raw_date
except Exception:
    lenders_list = []
    formatted_date = "27 Nov 2026"

lender_items_html = []
for lender in lenders_list:
    short_name = lender.get("short_name", lender.get("name", ""))
    lender_type = str(lender.get("type", "Bank")).lower()
    dot_class = "nbfc" if lender_type == "nbfc" else "bank"
    lender_items_html.append(
        f'<div class="lender-item">'
        f'  <span class="lender-dot {dot_class}"></span>'
        f'  <span>{short_name}</span>'
        f'</div>'
    )
lenders_grid_html = "".join(lender_items_html)

st.markdown(
    f'<div class="lenders-card">'
    f'  <div class="lenders-head">'
    f'    <h3 class="lenders-title">{t("lenders_card_title")}</h3>'
    f'    <span class="lenders-meta">{t("lenders_updated_text", date=formatted_date)}</span>'
    f'  </div>'
    f'  <div class="lenders-grid">'
    f'    {lenders_grid_html}'
    f'  </div>'
    f'  <div class="lenders-legend">'
    f'    <span class="leg-bank">● {t("legend_bank")}</span>'
    f'    <span class="leg-nbfc">● {t("legend_nbfc")}</span>'
    f'  </div>'
    f'</div>',
    unsafe_allow_html=True,
)

footer()
