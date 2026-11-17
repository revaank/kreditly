from __future__ import annotations

"""Branding, shared page chrome and reusable display components."""
import streamlit as st
import plotly.graph_objects as go
from .translations import t
from .finance import format_inr, loan_summary

CSS="""
<style>
@import url('https://fonts.googleapis.com/css2?family=Courgette&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Sora:wght@600;700&display=swap');
:root{--ink:#0F1B15;--navy:var(--ink);--lime:#C6F24E;--emerald:#1F7A4D;--red:#B63E32;--amber:#8A4B00;--muted:#4A554F;--line:#E2E5DC;--bg:#F5F6F1;--card:#FFFFFF}
html,body,[class*="css"]{font-family:Inter,Arial,sans-serif;color:var(--ink)}.stApp{background:var(--bg)}.block-container{max-width:1240px;padding:1.1rem 1.5rem 3rem}#MainMenu,footer{visibility:hidden}header[data-testid="stHeader"]{background:transparent}[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"]{display:none!important}
.brand{display:flex;align-items:center;gap:11px;text-decoration:none!important;color:var(--ink)!important;font-family:'Space Grotesk',sans-serif;font-size:23px;letter-spacing:-.03em;font-weight:700}.brand-mark{width:38px;height:38px;border-radius:12px;background:var(--ink);display:grid;place-items:center;color:var(--lime);font-family:'Space Grotesk',sans-serif;font-size:25px}
.topline{height:1px;background:var(--line);margin:14px 0 24px}.hero{padding:clamp(30px,7vw,80px) 0 45px;max-width:820px}.eyebrow{font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#52751e;margin-bottom:16px}h1{font-family:Sora,sans-serif;font-weight:600;letter-spacing:-.045em;line-height:1.1!important;font-size:clamp(36px,6vw,62px)!important;color:var(--navy)}.hero-copy{font-size:18px;line-height:1.65;color:var(--muted);max-width:690px}h2{font-family:Sora,sans-serif;letter-spacing:-.03em;font-size:25px!important}
.stSlider [data-testid="stSliderThumbValue"],.stSlider [data-testid="stSliderTickBarMin"],.stSlider [data-testid="stSliderTickBarMax"]{display:none!important}.stSlider:has([aria-label*="Repayment"]) [data-testid="stSliderTickBarMin"],.stSlider:has([aria-label*="Repayment"]) [data-testid="stSliderTickBarMax"],.stSlider:has([aria-label*="Repayment"]) [data-testid="stSliderThumbValue"],.stSlider:has([aria-label*="अवधि"]) [data-testid="stSliderTickBarMin"],.stSlider:has([aria-label*="अवधि"]) [data-testid="stSliderTickBarMax"],.stSlider:has([aria-label*="अवधि"]) [data-testid="stSliderThumbValue"],.stSlider:has([aria-valuetext*="month"]) [data-testid="stSliderTickBarMin"],.stSlider:has([aria-valuetext*="month"]) [data-testid="stSliderTickBarMax"],.stSlider:has([aria-valuetext*="month"]) [data-testid="stSliderThumbValue"],.stSlider:has([aria-valuetext*="महीने"]) [data-testid="stSliderTickBarMin"],.stSlider:has([aria-valuetext*="महीने"]) [data-testid="stSliderTickBarMax"],.stSlider:has([aria-valuetext*="महीने"]) [data-testid="stSliderThumbValue"]{display:block!important}
.feature-card,.step-card,.panel,.result-card,.case-card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:22px;box-shadow:0 8px 28px rgba(11,18,32,.045);height:100%}.panel{position:sticky;top:16px;z-index:1}.feature-icon{background:#F1F9DF;color:#52751e;width:40px;height:40px;border-radius:13px;display:grid;place-items:center;font-size:20px}.step-num{color:#5c8122;font-size:12px;font-weight:800;letter-spacing:.08em}.feature-card h3,.step-card h3{font-size:17px;margin:15px 0 6px}.feature-card p,.step-card p{font-size:14px;line-height:1.6;color:var(--muted)}.stButton>button,.stPageLink a{border-radius:999px!important;min-height:46px;padding:0 22px!important;font-weight:700!important;border:1px solid var(--line)!important}.stButton>button[kind="primary"],.stPageLink a[kind="primary"]{background:var(--navy)!important;color:white!important;border-color:var(--navy)!important}.stProgress>div>div>div{background:var(--lime)}
.result-card{border-top:5px solid var(--emerald);padding:25px;animation:fade-up .4s ease-out}.result-card.risky{border-top-color:var(--red)}.result-card.borderline{border-top-color:var(--amber)}@keyframes fade-up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}.risk-number{font-family:Sora,sans-serif;font-size:48px;font-weight:700;letter-spacing:-.05em}.risk-track,.afford-track{height:9px;background:#EEF1F5;border-radius:9px;overflow:hidden}.risk-fill,.afford-fill{height:100%;border-radius:9px;background:var(--emerald)}.risk-fill.risky,.afford-fill.high{background:var(--red)}.risk-fill.borderline,.afford-fill.watch{background:var(--amber)}.muted{color:var(--muted)}.footer{border-top:1px solid var(--line);margin-top:48px;padding-top:18px;color:var(--muted);font-size:12px;text-align:center}.small-label{font-size:12px;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.07em}.notice{background:#F0F6E7;border-radius:12px;padding:14px 16px;color:#435D1B;font-size:13px}
.bank-status{display:inline-block;border-radius:999px;padding:8px 12px;font-size:13px;font-weight:800;line-height:1.3;max-width:100%;white-space:normal}.bank-status.meets{background:#ECFCCB;color:#365314}.bank-status.close{background:#FEF3C7;color:#854D0E}.bank-status.not_yet{background:#FEE2E2;color:#991B1B}
.whatif-result{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px 16px;margin:10px 0}.whatif-result>strong{display:block;font-family:Sora,sans-serif;font-size:22px;margin:4px 0 8px}.delta-neutral{color:#667085}.delta-down{color:#1f7a4d;font-weight:700}.delta-up{color:#c36b0a;font-weight:700}
div[data-testid="stMarkdownContainer"] a{display:inline-flex;align-items:center;min-height:44px}
@media(max-width:720px){.block-container{padding:.9rem .85rem 2rem}div[data-testid="stHorizontalBlock"]{flex-direction:column!important;gap:12px!important}div[data-testid="column"]{width:100%!important;flex:1 1 100%!important}.hero{padding:36px 0 28px}.hero-copy{font-size:16px}.feature-card,.step-card,.panel,.case-card{padding:18px}.brand{font-size:20px}.risk-number{font-size:40px}}
.hero-pill{display:inline-flex;align-items:center;border:1px solid var(--line);background:#fff;border-radius:999px;padding:8px 13px;font-size:13px;font-weight:600;color:var(--muted);margin:12px 0 18px}.home-title{font-family:'Space Grotesk',sans-serif!important;font-size:clamp(38px,5vw,62px)!important;line-height:1.04!important;letter-spacing:-.045em!important;color:var(--ink)!important;margin:0 0 16px}.hero-copy{font-size:17px;line-height:1.65;color:var(--muted);max-width:670px}.trust-row{display:flex;flex-wrap:wrap;gap:8px 18px;margin:18px 0 25px;color:var(--muted);font-size:12px}.trust-row span{white-space:normal}.sample-result{background:var(--ink);color:#fff;border-radius:26px;padding:26px;border:1px solid #243229;box-shadow:0 18px 42px rgba(15,27,21,.12)}.sample-top{display:flex;justify-content:space-between;align-items:center;gap:10px;color:#D5DED8;font-size:12px}.sample-badge{background:var(--lime);color:var(--ink);border-radius:999px;padding:7px 11px;font-weight:700;font-size:11px}.sample-title{font-family:'Space Grotesk',sans-serif;font-size:29px;font-weight:700;margin:25px 0 13px}.sample-meter{height:9px;border-radius:99px;background:#34433A;overflow:hidden}.sample-meter span{display:block;height:100%;width:43%;background:var(--lime);border-radius:99px}.sample-stats{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:22px 0}.sample-stats>div{border:1px solid #35443A;border-radius:15px;padding:14px}.sample-stats small,.sample-fix small{display:block;color:#B9C5BD;font-size:11px;margin-bottom:7px}.sample-stats strong{font-family:'Space Grotesk',sans-serif;font-size:22px;color:#fff}.sample-fix{background:var(--lime);color:var(--ink);padding:15px;border-radius:15px}.sample-fix small{color:#34431A;font-weight:700}.sample-fix p{margin:0;line-height:1.45;font-size:13px}.lender-strip{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:17px 2px;margin:12px 0 48px;color:var(--muted)}.lender-strip span{font-size:12px}.lender-strip strong{font-size:14px;color:var(--ink)}.feature-card,.step-card,.panel,.result-card,.case-card{background:var(--card);border:1px solid var(--line);border-radius:22px;box-shadow:0 6px 24px rgba(15,27,21,.035)}.step-card{min-height:172px}.step-card h3,.feature-card h3{font-family:'Space Grotesk',sans-serif;color:var(--ink)}.step-num{color:#47611C}.feature-panel{background:var(--ink);color:#fff;border-radius:25px;padding:27px;margin:42px 0 25px}.feature-panel h2{font-family:'Space Grotesk',sans-serif;color:#fff;margin:0 0 23px}.feature-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:13px}.feature-grid article{border:1px solid #34433A;border-radius:17px;padding:17px;min-height:162px}.feature-grid article>span{color:var(--lime);font-size:12px;font-weight:700}.feature-grid h3{color:#fff;font-family:'Space Grotesk',sans-serif;font-size:16px;margin:14px 0 8px}.feature-grid p{color:#C3CEC6;font-size:12px;line-height:1.5;margin:0}.stButton>button,.stPageLink a,.stLinkButton a{border-radius:13px!important;min-height:46px;padding:0 16px!important;font-weight:600!important}.stPageLink a[kind="primary"],.stButton>button[kind="primary"]{background:var(--ink)!important;color:#fff!important;border-color:var(--ink)!important}.stPageLink a:not([kind="primary"]),.stLinkButton a{background:#fff!important;color:var(--ink)!important;border-color:var(--line)!important}.stProgress>div>div>div{background:var(--lime)}.footer{color:var(--muted)}
@media(max-width:720px){.block-container{padding:.8rem .85rem 2rem}.home-title{font-size:39px!important}.sample-result{padding:21px;border-radius:21px}.lender-strip{justify-content:flex-start}.feature-grid{grid-template-columns:1fr 1fr}.feature-panel{padding:21px 16px}.feature-grid article{min-height:145px}.trust-row{gap:8px 12px}.stButton>button,.stPageLink a,.stLinkButton a{min-height:48px}button[key="toggle_language"],button[kind="secondary"]{white-space:nowrap!important;min-width:68px!important;padding:0 8px!important}}
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
    if "language" not in st.session_state: st.session_state.language="EN"
    toggle_label = "हिन्दी" if st.session_state.language == "EN" else "English"
    a,b=st.columns([3.6,6.4])
    with a: st.markdown('<a class="brand" href="/"><span class="brand-mark">k</span><span>kreditly</span></a>',unsafe_allow_html=True)
    with b:
        x,y,z,i,l=st.columns([1.0,1.2,1.3,1.7,1.2])
        def _safe_link(page, label):
            try:
                st.page_link(page, label=label)
            except Exception:
                st.markdown(f'<a href="/">{label}</a>', unsafe_allow_html=True)
        with x: _safe_link("app.py", t("nav_home"))
        with y: _safe_link("pages/1_Check_Eligibility.py", t("nav_check"))
        with z: _safe_link("pages/2_Sample_Cases.py", t("nav_samples"))
        with i: _safe_link("pages/3_Model_Insights.py", t("nav_insights"))
        with l:
            if st.button(toggle_label,key="toggle_language",use_container_width=True,on_click=_toggle_language):
                st.rerun()
    st.markdown('<div class="topline"></div>',unsafe_allow_html=True)

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
def footer(): st.markdown(f'<div class="footer">{t("footer")}</div>',unsafe_allow_html=True)
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
        report_lines.extend(f'{item["name"]}: {t("bank_status_" + item["status"])}' for item in bank_results)
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
