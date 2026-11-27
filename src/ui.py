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
  --navy: var(--ink);
  --lime: var(--accent);
  --emerald: var(--good);
  --amber: var(--warn);
  --red: var(--bad);
}

html, body, [class*="css"] {
  font-family: 'Inter', 'Mukta', sans-serif;
  color: var(--ink);
}

.stApp {
  background:
    radial-gradient(900px 520px at 82% 6%, rgba(198,242,78,.45), transparent 60%),
    radial-gradient(700px 480px at 4% 36%, rgba(31,122,77,.12), transparent 62%),
    radial-gradient(800px 600px at 96% 80%, rgba(198,242,78,.22), transparent 60%),
    #F5F6F1;
  background-attachment: fixed;
  color: var(--ink);
}

.stApp::before {
  content: "";
  background-image: radial-gradient(rgba(15,27,21,.14) 1px, transparent 1.3px);
  background-size: 22px 22px;
  mask-image: linear-gradient(to bottom, #000 0%, rgba(0,0,0,.5) 30%, transparent 60%);
  -webkit-mask-image: linear-gradient(to bottom, #000 0%, rgba(0,0,0,.5) 30%, transparent 60%);
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
.main,
.block-container {
  background: transparent !important;
}

.block-container {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  padding: 1.2rem 1.5rem 3.5rem;
}

#MainMenu, footer {
  visibility: hidden;
}

header[data-testid="stHeader"] {
  background: transparent !important;
}

[data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] {
  display: none !important;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  font-family: 'Space Grotesk', 'Mukta', sans-serif !important;
  color: var(--ink) !important;
  letter-spacing: -0.025em;
}

p, span, label, div {
  font-family: 'Inter', 'Mukta', sans-serif;
}

small, .muted, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
  color: var(--muted) !important;
}

/* Brand */
.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  text-decoration: none !important;
  color: var(--ink) !important;
  font-family: 'Space Grotesk', 'Mukta', sans-serif;
  font-size: 22px;
  letter-spacing: -0.03em;
  font-weight: 700;
}

.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: var(--ink);
  display: grid;
  place-items: center;
  color: var(--accent);
  font-family: 'Space Grotesk', sans-serif;
  font-size: 22px;
  line-height: 1;
  font-weight: 700;
}

.topline {
  height: 1px;
  background: var(--line);
  margin: 14px 0 32px;
}

/* Cards */
.feature-card, .step-card, .panel, .result-card, .case-card, [data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 20px;
  box-shadow: 0 4px 16px rgba(15,27,21,.025);
}

.panel {
  position: sticky;
  top: 16px;
  z-index: 1;
}

/* Navigation items in header */
.header-container {
  margin-bottom: 2px;
}
.header-nav-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 28px;
}
.nav-item div[data-testid="stPageLink-NavLink"] a,
.nav-item a {
  background: transparent !important;
  border: none !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  padding: 6px 2px !important;
  min-height: auto !important;
  height: auto !important;
  font-family: 'Inter', 'Mukta', sans-serif !important;
  font-size: 15px !important;
  display: inline-flex !important;
  justify-content: center !important;
  white-space: nowrap !important;
}
.nav-item.nav-link-idle div[data-testid="stPageLink-NavLink"] a,
.nav-item.nav-link-idle a {
  color: var(--muted) !important;
  font-weight: 500 !important;
  border-bottom: 2px solid transparent !important;
}
.nav-item.nav-link-idle div[data-testid="stPageLink-NavLink"] a:hover,
.nav-item.nav-link-idle a:hover {
  color: var(--ink) !important;
}
.nav-item.nav-link-active div[data-testid="stPageLink-NavLink"] a,
.nav-item.nav-link-active a {
  color: var(--ink) !important;
  font-weight: 600 !important;
  border-bottom: 2px solid var(--ink) !important;
}

/* Language switch */
.header-lang-wrap {
  display: flex;
  justify-content: flex-end;
}
.header-lang-wrap button[key="toggle_language"],
.header-lang-wrap button[data-testid="stBaseButton-secondary"] {
  background: var(--soft) !important;
  border: 1px solid var(--line) !important;
  border-radius: 999px !important;
  padding: 3px 6px !important;
  min-height: 36px !important;
  height: 36px !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  box-shadow: none !important;
  color: var(--muted) !important;
}
.header-lang-wrap button[key="toggle_language"]:hover,
.header-lang-wrap button[data-testid="stBaseButton-secondary"]:hover {
  background: #E5E8E0 !important;
  border-color: #D7DCCF !important;
}
.header-lang-wrap.lang-en button p {
  color: var(--muted) !important;
}
.header-lang-wrap.lang-en button strong {
  background: var(--ink) !important;
  color: #FFFFFF !important;
  padding: 4px 10px !important;
  border-radius: 999px !important;
  margin-right: 2px !important;
  display: inline-block !important;
}
.header-lang-wrap.lang-hi button p {
  color: var(--muted) !important;
}
.header-lang-wrap.lang-hi button strong {
  background: var(--ink) !important;
  color: #FFFFFF !important;
  padding: 4px 10px !important;
  border-radius: 999px !important;
  margin-left: 2px !important;
  display: inline-block !important;
}

/* Mobile header */
@media (max-width: 640px) {
  .header-container > div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-wrap: wrap !important;
    justify-content: space-between !important;
    align-items: center !important;
  }
  .header-container div[data-testid="column"]:has(.header-brand-wrap) {
    order: 1 !important;
    flex: 1 1 auto !important;
    width: auto !important;
  }
  .header-container div[data-testid="column"]:has(.header-lang-wrap) {
    order: 2 !important;
    flex: 0 0 auto !important;
    width: auto !important;
  }
  .header-container div[data-testid="column"]:has(.header-nav-wrap) {
    order: 3 !important;
    flex: 0 0 100% !important;
    width: 100% !important;
    overflow-x: auto !important;
    margin-top: 10px !important;
    padding-bottom: 4px !important;
  }
  .header-nav-wrap {
    justify-content: flex-start !important;
    gap: 20px !important;
    min-width: 290px !important;
  }
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

/* Global button styling */
.stButton>button, .stPageLink a, .stLinkButton a {
  border-radius: 14px !important;
  min-height: 46px;
  padding: 0 20px !important;
  font-weight: 600 !important;
  font-family: 'Inter', 'Mukta', sans-serif !important;
}
.stButton>button[kind="primary"], .stButton>button[data-testid="stBaseButton-primary"] {
  background: var(--ink) !important;
  color: #FFFFFF !important;
  border: 1px solid var(--ink) !important;
}

/* Hero CTA specific button */
.st-key-hero_cta button, .st-key-hero_cta div[data-testid="stBaseButton-primary"] {
  background: var(--accent) !important;
  color: var(--ink) !important;
  font-weight: 700 !important;
  font-size: 17px !important;
  padding: 18px 30px !important;
  border-radius: 14px !important;
  border: none !important;
  box-shadow: 0 10px 24px -12px rgba(90,120,10,.55) !important;
  min-height: 54px !important;
  transition: all 0.2s ease !important;
}
.st-key-hero_cta button:hover, .st-key-hero_cta div[data-testid="stBaseButton-primary"]:hover {
  background: #B8E63A !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 12px 28px -10px rgba(90,120,10,.6) !important;
}
.st-key-hero_cta button p, .st-key-hero_cta button span {
  color: var(--ink) !important;
  font-weight: 700 !important;
}

/* Result Cards and Badges */
.bank-status {
  display: inline-block;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 700;
}
.bank-status.meets { background: #ECFCCB; color: #365314; }
.bank-status.close { background: #FEF3C7; color: #854D0E; }
.bank-status.limited { background: #F3F4F6; color: #4B5563; }
.bank-status.not_yet { background: #FEE2E2; color: #991B1B; }

/* Sliders */
.stSlider [data-testid="stSliderThumbValue"],.stSlider [data-testid="stSliderTickBarMin"],.stSlider [data-testid="stSliderTickBarMax"]{display:none!important}
.stSlider:has([aria-label*="Repayment"]) [data-testid="stSliderTickBarMin"],.stSlider:has([aria-label*="Repayment"]) [data-testid="stSliderTickBarMax"],.stSlider:has([aria-label*="Repayment"]) [data-testid="stSliderThumbValue"],.stSlider:has([aria-label*="अवधि"]) [data-testid="stSliderTickBarMin"],.stSlider:has([aria-label*="अवधि"]) [data-testid="stSliderTickBarMax"],.stSlider:has([aria-label*="अवधि"]) [data-testid="stSliderThumbValue"],.stSlider:has([aria-valuetext*="month"]) [data-testid="stSliderTickBarMin"],.stSlider:has([aria-valuetext*="month"]) [data-testid="stSliderTickBarMax"],.stSlider:has([aria-valuetext*="month"]) [data-testid="stSliderThumbValue"],.stSlider:has([aria-valuetext*="महीने"]) [data-testid="stSliderTickBarMin"],.stSlider:has([aria-valuetext*="महीने"]) [data-testid="stSliderTickBarMax"],.stSlider:has([aria-valuetext*="महीने"]) [data-testid="stSliderThumbValue"]{display:block!important}

/* Footer */
.footer-wrap {
  border-top: 1px solid var(--line);
  margin-top: 64px;
  padding-top: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 13px;
  color: var(--muted);
}
.footer-left {
  color: var(--muted);
}
.footer-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.footer-right a {
  color: var(--muted);
  text-decoration: underline;
  text-underline-offset: 2px;
  transition: color 0.15s ease;
}
.footer-right a:hover {
  color: var(--ink);
}
.footer-sep {
  color: var(--line);
}
@media (max-width: 640px) {
  .footer-wrap {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
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

    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    col_logo, col_nav, col_lang = st.columns([2.0, 6.2, 1.8], vertical_alignment="center")

    with col_logo:
        st.markdown(
            '<div class="header-brand-wrap">'
            '<a class="brand" href="/" target="_self">'
            '<span class="brand-mark">k</span>'
            '<span>kreditly</span>'
            '</a>'
            '</div>',
            unsafe_allow_html=True,
        )

    with col_nav:
        st.markdown('<div class="header-nav-wrap">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)

        def _render_nav_item(col, page, label, is_act):
            cls = "nav-link-active" if is_act else "nav-link-idle"
            with col:
                st.markdown(f'<div class="nav-item {cls}">', unsafe_allow_html=True)
                try:
                    st.page_link(page, label=label)
                except Exception:
                    href = "/" + page.split("/")[-1].replace(".py", "")
                    st.markdown(f'<a href="{href}">{label}</a>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        _render_nav_item(c1, "pages/1_Check_Eligibility.py", t("nav_check"), active == "check")
        _render_nav_item(c2, "pages/4_Tools.py", t("nav_tools"), active == "tools")
        _render_nav_item(c3, "pages/5_Guide.py", t("nav_guide"), active == "guide")
        _render_nav_item(c4, "pages/2_Sample_Cases.py", t("nav_samples"), active == "samples")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_lang:
        cls_lang = "lang-en" if cur_lang == "EN" else "lang-hi"
        st.markdown(f'<div class="header-lang-wrap lang-pill-wrap {cls_lang}">', unsafe_allow_html=True)
        btn_label = "**EN** | हिं" if cur_lang == "EN" else "EN | **हिं**"
        if st.button(btn_label, key="toggle_language", use_container_width=True, on_click=_toggle_language):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div><div class="topline"></div>', unsafe_allow_html=True)

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
        f'<div class="footer-wrap">'
        f'<div class="footer-left">{t("footer_built_by")}</div>'
        f'<div class="footer-right">'
        f'<a href="/Model_Insights" target="_self">{t("footer_how_models_work")}</a>'
        f'<span class="footer-sep">·</span>'
        f'<a href="/About" target="_self">{t("footer_about_privacy")}</a>'
        f'</div>'
        f'</div>',
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
