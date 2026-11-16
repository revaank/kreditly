"""Branding, shared page chrome and reusable display components."""
import streamlit as st
import plotly.graph_objects as go
from .translations import t
from .finance import format_inr

CSS="""
<style>
@import url('https://fonts.googleapis.com/css2?family=Courgette&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Sora:wght@600;700&display=swap');
:root{--navy:#0B1220;--lime:#A3E635;--emerald:#34D399;--red:#F87171;--amber:#FCD34D;--muted:#667085;--line:#E8ECF2;--bg:#F5F7FA}
html,body,[class*="css"]{font-family:'Plus Jakarta Sans',sans-serif;color:var(--navy)}.stApp{background:var(--bg)}.block-container{max-width:1180px;padding:1.4rem 1.4rem 3rem}#MainMenu,footer{visibility:hidden}header[data-testid="stHeader"]{background:transparent}
.brand{display:flex;align-items:center;gap:11px;text-decoration:none!important;color:var(--navy)!important;font-family:Sora,sans-serif;font-size:23px;letter-spacing:-.03em;font-weight:600}.brand-mark{width:38px;height:38px;border-radius:12px;background:var(--navy);display:grid;place-items:center;color:var(--lime);font-family:Courgette,cursive;font-size:25px}
.topline{height:1px;background:var(--line);margin:14px 0 24px}.hero{padding:clamp(30px,7vw,80px) 0 45px;max-width:820px}.eyebrow{font-size:12px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#52751e;margin-bottom:16px}h1{font-family:Sora,sans-serif;font-weight:600;letter-spacing:-.045em;line-height:1.1!important;font-size:clamp(36px,6vw,62px)!important;color:var(--navy)}.hero-copy{font-size:18px;line-height:1.65;color:var(--muted);max-width:690px}h2{font-family:Sora,sans-serif;letter-spacing:-.03em;font-size:25px!important}
.stSlider [data-testid="stSliderThumbValue"],.stSlider [data-testid="stSliderTickBarMin"],.stSlider [data-testid="stSliderTickBarMax"]{display:none!important}
.feature-card,.step-card,.panel,.result-card,.case-card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:22px;box-shadow:0 8px 28px rgba(11,18,32,.045);height:100%}.panel{position:sticky;top:16px;z-index:1}.feature-icon{background:#F1F9DF;color:#52751e;width:40px;height:40px;border-radius:13px;display:grid;place-items:center;font-size:20px}.step-num{color:#5c8122;font-size:12px;font-weight:800;letter-spacing:.08em}.feature-card h3,.step-card h3{font-size:17px;margin:15px 0 6px}.feature-card p,.step-card p{font-size:14px;line-height:1.6;color:var(--muted)}.stButton>button,.stPageLink a{border-radius:999px!important;min-height:46px;padding:0 22px!important;font-weight:700!important;border:1px solid var(--line)!important}.stButton>button[kind="primary"],.stPageLink a[kind="primary"]{background:var(--navy)!important;color:white!important;border-color:var(--navy)!important}.stProgress>div>div>div{background:var(--lime)}
.result-card{border-top:5px solid var(--emerald);padding:25px;animation:fade-up .4s ease-out}.result-card.risky{border-top-color:var(--red)}.result-card.borderline{border-top-color:var(--amber)}@keyframes fade-up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}.risk-number{font-family:Sora,sans-serif;font-size:48px;font-weight:700;letter-spacing:-.05em}.risk-track,.afford-track{height:9px;background:#EEF1F5;border-radius:9px;overflow:hidden}.risk-fill,.afford-fill{height:100%;border-radius:9px;background:var(--emerald)}.risk-fill.risky,.afford-fill.high{background:var(--red)}.risk-fill.borderline,.afford-fill.watch{background:var(--amber)}.muted{color:var(--muted)}.footer{border-top:1px solid var(--line);margin-top:48px;padding-top:18px;color:var(--muted);font-size:12px;text-align:center}.small-label{font-size:12px;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.07em}.notice{background:#F0F6E7;border-radius:12px;padding:14px 16px;color:#435D1B;font-size:13px}
@media(max-width:720px){.block-container{padding:.9rem .85rem 2rem}div[data-testid="stHorizontalBlock"]{flex-direction:column!important;gap:12px!important}div[data-testid="column"]{width:100%!important;flex:1 1 100%!important}.hero{padding:36px 0 28px}.hero-copy{font-size:16px}.feature-card,.step-card,.panel,.case-card{padding:18px}.brand{font-size:20px}.risk-number{font-size:40px}}
</style>"""

def page_setup():
    st.set_page_config(page_title="Kreditly · Loan readiness",page_icon="🟩",layout="wide",initial_sidebar_state="collapsed")
    st.markdown(CSS,unsafe_allow_html=True)

def _toggle_language():
    """Switch between English and Hindi before page text is rendered."""
    st.session_state.language="हिं" if st.session_state.language=="EN" else "EN"

def header(active=""):
    if "language" not in st.session_state: st.session_state.language="EN"
    a,b=st.columns([5,4])
    with a: st.markdown('<a class="brand" href="/"><span class="brand-mark">k</span><span>kreditly</span></a>',unsafe_allow_html=True)
    with b:
        x,y,z,i,l=st.columns([.9,1.05,1.05,1,.9])
        with x: st.page_link("app.py",label=t("nav_home"))
        with y: st.page_link("pages/1_Check_Eligibility.py",label=t("nav_check"))
        with z: st.page_link("pages/2_Sample_Cases.py",label=t("nav_samples"))
        with i: st.page_link("pages/3_Model_Insights.py",label=t("nav_insights"))
        with l: st.button("EN | हिं",key="toggle_language",help=t("language"),use_container_width=True,on_click=_toggle_language)
    st.markdown('<div class="topline"></div>',unsafe_allow_html=True)
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

def result_card(result):
    tone=result["label"].lower(); title={"STRONG":t("strong"),"BORDERLINE":t("borderline"),"RISKY":t("risky")}[result["label"]]; risk=round(result["risk"]*100)
    st.markdown(f'<div class="result-card {tone}"><div class="small-label">{title}</div><div class="risk-number">{risk}%</div><div class="muted">{t("risk")}</div><div style="height:14px"></div><div class="risk-track"><div class="risk-fill {tone}" style="width:{risk}%"></div></div><div style="height:14px"></div><div class="muted">{t("dummy_notice")}</div></div>',unsafe_allow_html=True)
