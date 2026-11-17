"""Kreditly's home page for an educational historical-model demonstration."""
import json
from pathlib import Path

import streamlit as st

from src.bank_checker import check_all, count_meets
from src.counterfactual import find_improvements
from src.explainer import suggestion_text
from src.features import build_features
from src.finance import format_inr, loan_summary
from src.predictor import predict
from src.translations import t
from src.ui import footer, header, page_setup, section_title

HOME_COPY = {
    "EN": {
        "pill": "Free · 2 minutes · No sign-up",
        "title": "Know where you stand before a bank says no.",
        "subtext": "Explore a loan-readiness estimate, compare published lender criteria, and see practical next steps. This is educational information, not a credit decision.",
        "example": "See an example result",
        "trust1": "Doesn't touch your CIBIL score",
        "trust2": "Your details stay in this session",
        "trust3": "Source links for lender rules",
        "sample": "Example result",
        "lenders": "Lender criteria matched",
        "fix": "A practical next step",
        "sample_fix": "Consider a smaller loan amount to reduce the monthly EMI.",
        "sample_good_note": "Low credit card limit usage and steady employment support this profile.",
        "lender_caption": "Published criteria from six lenders",
        "features_title": "A clearer first step",
        "feature1": "Published lender criteria",
        "feature1_body": "Compare your details with the rules and source links we have.",
        "feature2": "Practical next steps",
        "feature2_body": "Explore different ways to improve affordability before applying.",
        "feature3": "What-if planner",
        "feature3_body": "Change loan details and see how the estimate and lender matches respond.",
        "feature4": "EMI planner",
        "feature4_body": "Compare estimated monthly payments across repayment periods.",
    },
    "हिं": {
        "pill": "मुफ़्त · 2 मिनट · साइन अप नहीं",
        "title": "बैंक के मना करने से पहले अपनी स्थिति समझें।",
        "subtext": "ऋण तैयारी का अनुमान देखें, प्रकाशित ऋणदाता मानदंडों की तुलना करें और व्यावहारिक अगले कदम जानें। यह शैक्षिक जानकारी है, क्रेडिट निर्णय नहीं।",
        "example": "उदाहरण परिणाम देखें",
        "trust1": "आपका CIBIL स्कोर प्रभावित नहीं होता",
        "trust2": "आपकी जानकारी इसी सेशन में रहती है",
        "trust3": "ऋणदाता नियमों के स्रोत लिंक",
        "sample": "उदाहरण परिणाम",
        "lenders": "ऋणदाता मानदंड पूरे",
        "fix": "एक व्यावहारिक अगला कदम",
        "sample_fix": "मासिक EMI घटाने के लिए कम ऋण राशि पर विचार करें।",
        "sample_good_note": "कम कार्ड उपयोग और नियमित रोज़गार इस प्रोफ़ाइल को मज़बूत बनाते हैं।",
        "lender_caption": "छह ऋणदाताओं के प्रकाशित मानदंड",
        "features_title": "एक बेहतर शुरुआत",
        "feature1": "प्रकाशित ऋणदाता मानदंड",
        "feature1_body": "अपनी जानकारी की उपलब्ध नियमों और स्रोत लिंक से तुलना करें।",
        "feature2": "व्यावहारिक अगले कदम",
        "feature2_body": "आवेदन से पहले भुगतान क्षमता बेहतर करने के अलग-अलग तरीके देखें।",
        "feature3": "क्या हो अगर प्लानर",
        "feature3_body": "ऋण विवरण बदलें और अनुमान तथा ऋणदाता मिलान में बदलाव देखें।",
        "feature4": "EMI प्लानर",
        "feature4_body": "अलग-अलग भुगतान अवधियों की अनुमानित मासिक किस्त की तुलना करें।",
    },
}


def home_text(key: str) -> str:
    language = st.session_state.get("language", "EN")
    return HOME_COPY.get(language, HOME_COPY["EN"])[key]


@st.cache_data(show_spinner=False)
def _sample_preview_data():
    profile = {
        "age": 32, "employment": "Salaried", "job_years": 6, "home": "own_loan",
        "credit_year": 2010, "annual_income": 1200000, "existing_emi": 5000,
        "card_bill": 10000, "revol_util": 5, "open_acc": 5, "total_acc": 15,
        "mort_acc": 1, "pub_rec": 0, "bankruptcies": 0, "cibil": "Good · 700–749",
        "loan_amount": 300000, "tenure_months": 36, "purpose": "debt_consolidation", "rate": 11.0,
    }
    features = build_features(profile)
    estimate = predict(features)
    bank_results = check_all(profile)
    summary = loan_summary(profile["loan_amount"], profile["rate"], profile["tenure_months"])
    improvements = find_improvements(profile, max_suggestions=1)
    return {
        "band": estimate.get("readiness_band", "good"),
        "risk": float(estimate.get("risk", 0.0)),
        "meets": count_meets(bank_results),
        "total_lenders": len(bank_results),
        "emi": summary["emi"],
        "improvements": improvements,
    }


page_setup()
header("home")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
.stApp{background:#F5F6F1;color:#0F1B15;font-family:Inter,Arial,sans-serif}.block-container{max-width:1240px;padding:1.1rem 1.5rem 3rem}.brand{font:700 23px 'Space Grotesk',sans-serif!important;color:#0F1B15!important}.brand-mark{background:#0F1B15!important;color:#C6F24E!important}.topline{background:#E2E5DC!important}[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"]{display:none!important}
.home-title{font-family:'Space Grotesk',sans-serif!important;font-size:clamp(38px,5vw,62px)!important;line-height:1.04!important;letter-spacing:-.045em!important;color:#0F1B15!important;margin:0 0 16px}
.hero-copy{font:400 17px/1.65 Inter,Arial,sans-serif;color:#4A554F;max-width:670px}.hero-pill{display:inline-flex;background:#fff;border:1px solid #E2E5DC;border-radius:999px;padding:8px 13px;margin:12px 0 18px;color:#4A554F;font-size:13px;font-weight:600}
.trust-row{display:flex;flex-wrap:wrap;gap:8px 18px;margin:18px 0 25px;color:#4A554F;font-size:12px}.sample-result{background:#0F1B15;color:#fff;border:1px solid #293A30;border-radius:26px;padding:26px;box-shadow:0 18px 42px rgba(15,27,21,.12)}
.sample-top{display:flex;justify-content:space-between;align-items:center;gap:10px;color:#D5DED8;font-size:12px}.sample-badge{background:#C6F24E;color:#0F1B15;border-radius:999px;padding:7px 11px;font-weight:700;font-size:11px}.sample-title{font:700 29px 'Space Grotesk',sans-serif;margin:25px 0 13px}
.sample-meter{height:9px;border-radius:99px;background:#34433A;overflow:hidden}.sample-meter span{display:block;height:100%;background:#C6F24E;border-radius:99px}.sample-stats{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:22px 0}.sample-stats>div{border:1px solid #35443A;border-radius:15px;padding:14px}.sample-stats small,.sample-fix small{display:block;color:#B9C5BD;font-size:11px;margin-bottom:7px}.sample-stats strong{font:700 22px 'Space Grotesk',sans-serif;color:#fff}
.sample-fix{background:#C6F24E;color:#0F1B15;padding:15px;border-radius:15px}.sample-fix small{color:#34431A;font-weight:700}.sample-fix p{margin:0;line-height:1.45;font-size:13px}.lender-strip{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;border-block:1px solid #E2E5DC;padding:17px 2px;margin:12px 0 48px;color:#4A554F}.lender-strip span{font-size:12px}.lender-strip strong{font-size:14px;color:#0F1B15}
.feature-panel{background:#0F1B15;color:#fff;border-radius:25px;padding:27px;margin:42px 0 25px}.feature-panel h2{font:700 25px 'Space Grotesk',sans-serif;color:#fff;margin:0 0 23px}.feature-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:13px}.feature-grid article{border:1px solid #34433A;border-radius:17px;padding:17px;min-height:162px}.feature-grid article>span{color:#C6F24E;font-size:12px;font-weight:700}.feature-grid h3{color:#fff;font:600 16px 'Space Grotesk',sans-serif;margin:14px 0 8px}.feature-grid p{color:#C3CEC6;font-size:12px;line-height:1.5;margin:0}
.stPageLink a,.stButton>button{min-height:46px!important;border-radius:13px!important}.stPageLink a[kind="primary"],.stButton>button[kind="primary"]{background:#0F1B15!important;border-color:#0F1B15!important;color:#fff!important}
@media(max-width:720px){.block-container{padding:.8rem .85rem 2rem}.home-title{font-size:39px!important}.sample-result{padding:21px;border-radius:21px}.lender-strip{justify-content:flex-start}.feature-grid{grid-template-columns:1fr 1fr}.feature-panel{padding:21px 16px}.feature-grid article{min-height:145px}.trust-row{gap:8px 12px}.stPageLink a,.stButton>button{min-height:48px!important}}
</style>
""", unsafe_allow_html=True)

hero, preview = st.columns([1.15, 0.85], gap="large", vertical_alignment="center")
with hero:
    st.markdown(
        f'<div class="hero-pill">{home_text("pill")}</div>'
        f'<h1 class="home-title">{home_text("title")}</h1>'
        f'<p class="hero-copy">{home_text("subtext")}</p>',
        unsafe_allow_html=True,
    )
    primary, secondary = st.columns(2, gap="small")
    with primary:
        st.page_link("pages/1_Check_Eligibility.py", label=t("start_check"), icon=":material/arrow_forward:", use_container_width=True)
    with secondary:
        st.page_link("pages/2_Sample_Cases.py", label=home_text("example"), use_container_width=True)
    st.markdown(
        f'<div class="trust-row"><span>✓ {home_text("trust1")}</span>'
        f'<span>✓ {home_text("trust2")}</span><span>✓ {home_text("trust3")}</span></div>',
        unsafe_allow_html=True,
    )

with preview:
    sample_data = _sample_preview_data()
    band_label = t(f"readiness_{sample_data['band']}")
    risk_pct = round(sample_data["risk"] * 100)
    meter_width = max(6, min(100, risk_pct)) if risk_pct > 0 else 6
    if sample_data["improvements"]:
        fix_content = " + ".join(suggestion_text(change) for change in sample_data["improvements"][0]["changes"])
    else:
        fix_content = home_text("sample_good_note")

    st.markdown(
        f'<section class="sample-result"><div class="sample-top"><span>{home_text("sample")}</span>'
        f'<span class="sample-badge">{band_label}</span></div>'
        f'<div class="sample-title">{band_label}</div>'
        f'<div class="sample-meter"><span style="width:{meter_width}%"></span></div>'
        f'<div class="sample-stats"><div><small>{home_text("lenders")}</small><strong>{sample_data["meets"]} / {sample_data["total_lenders"]}</strong></div>'
        f'<div><small>{t("monthly_emi")}</small><strong>{format_inr(sample_data["emi"])}</strong></div></div>'
        f'<div class="sample-fix"><small>{home_text("fix")}</small><p>{fix_content}</p></div></section>',
        unsafe_allow_html=True,
    )

st.markdown(
    f'<div class="lender-strip"><span>{home_text("lender_caption")}</span>'
    '<strong>SBI</strong><strong>HDFC Bank</strong><strong>ICICI Bank</strong>'
    '<strong>Axis Bank</strong><strong>Bajaj Finance</strong><strong>Tata Capital</strong></div>',
    unsafe_allow_html=True,
)

section_title(t("how_title"))
steps = [
    ("01", t("step1"), t("step1_body")),
    ("02", t("step2"), t("step2_body")),
    ("03", t("step3"), t("step3_body")),
]
for col, (number, title, body) in zip(st.columns(3, gap="medium"), steps):
    with col:
        st.markdown(
            f'<article class="feature-card step-card"><span class="step-num">{number}</span>'
            f'<h3>{title}</h3><p>{body}</p></article>',
            unsafe_allow_html=True,
        )

st.markdown(f'<section class="feature-panel"><h2>{home_text("features_title")}</h2><div class="feature-grid">'
            f'<article><span>01</span><h3>{home_text("feature1")}</h3><p>{home_text("feature1_body")}</p></article>'
            f'<article><span>02</span><h3>{home_text("feature2")}</h3><p>{home_text("feature2_body")}</p></article>'
            f'<article><span>03</span><h3>{home_text("feature3")}</h3><p>{home_text("feature3_body")}</p></article>'
            f'<article><span>04</span><h3>{home_text("feature4")}</h3><p>{home_text("feature4_body")}</p></article>'
            '</div></section>', unsafe_allow_html=True)

st.info(t("model_warning"), icon="ℹ️")
footer()
