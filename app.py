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
.stApp{background:#F5F6F1;color:#0F1B15;font-family:Inter,Arial,sans-serif}.block-container{max-width:980px;padding:1.5rem 1.5rem 3.5rem}.brand{font:700 23px 'Space Grotesk',sans-serif!important;color:#0F1B15!important}.brand-mark{background:#0F1B15!important;color:#C6F24E!important}.topline{background:#E2E5DC!important}[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"]{display:none!important}
.hero-box{text-align:center;padding:40px 10px 24px;max-width:780px;margin:0 auto}
.home-title{font-family:'Space Grotesk',sans-serif!important;font-size:clamp(38px,5vw,56px)!important;line-height:1.08!important;letter-spacing:-.045em!important;color:#0F1B15!important;margin:0 0 16px}
.hero-copy{font:400 18px/1.6 Inter,Arial,sans-serif;color:#4A554F;max-width:640px;margin:0 auto 28px}
.hero-pill{display:inline-flex;background:#fff;border:1px solid #E2E5DC;border-radius:999px;padding:8px 16px;margin:0 auto 20px;color:#4A554F;font-size:13px;font-weight:600}
.cta-wrap{max-width:340px;margin:0 auto 14px}
.sample-link-wrap{text-align:center;margin:8px 0 28px;font-size:13px}
.sample-link-wrap a{color:#4A554F;text-decoration:underline}
.trust-row{display:flex;flex-wrap:wrap;justify-content:center;gap:12px 24px;margin:18px auto 44px;color:#4A554F;font-size:13px;text-align:center}
.lender-strip{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;border-block:1px solid #E2E5DC;padding:16px 4px;margin:28px 0 42px;color:#4A554F}
.lender-strip span{font-size:12px}
.lender-strip strong{font-size:14px;color:#0F1B15}
.step-card{background:#fff;border:1px solid #E2E5DC;border-radius:20px;padding:24px;height:100%;box-shadow:0 6px 20px rgba(15,27,21,.03)}
.step-num{color:#47611C;font-size:12px;font-weight:800;letter-spacing:.08em}
.step-card h3{font:700 18px 'Space Grotesk',sans-serif;margin:12px 0 6px;color:#0F1B15}
.step-card p{font-size:14px;line-height:1.55;color:#4A554F;margin:0}
.stPageLink a,.stButton>button{min-height:52px!important;border-radius:14px!important;font-weight:700!important}
.stPageLink a[kind="primary"],.stButton>button[kind="primary"],.stButton>button[data-testid="stBaseButton-primary"]{background:#0F1B15!important;border:1px solid #0F1B15!important;color:#ffffff!important;font-size:16px!important;font-weight:700!important;box-shadow:0 4px 14px rgba(15,27,21,.2)!important}
.stButton>button[kind="primary"]:hover,.stButton>button[data-testid="stBaseButton-primary"]:hover{background:#1f3328!important;border-color:#1f3328!important;color:#ffffff!important}
.stButton>button[kind="primary"] *,.stButton>button[data-testid="stBaseButton-primary"] *{color:#ffffff!important}
@media(max-width:720px){.block-container{padding:1rem .9rem 2.5rem}.home-title{font-size:36px!important}.hero-copy{font-size:16px}.trust-row{flex-direction:column;gap:8px;align-items:center}.lender-strip{justify-content:center;gap:10px}.cta-wrap{max-width:100%}div[data-testid="stHorizontalBlock"]{flex-direction:column!important;gap:14px!important}div[data-testid="column"]{width:100%!important;flex:1 1 100%!important}}
</style>
""", unsafe_allow_html=True)

st.markdown(
    f'<div class="hero-box">'
    f'<div class="hero-pill">{home_text("pill")}</div>'
    f'<h1 class="home-title">{home_text("title")}</h1>'
    f'<p class="hero-copy">{home_text("subtext")}</p>'
    f'</div>',
    unsafe_allow_html=True,
)

c_left, c_cta, c_right = st.columns([1, 1.4, 1])
with c_cta:
    if st.button(t("start_check"), type="primary", use_container_width=True, icon=":material/arrow_forward:"):
        st.switch_page("pages/1_Check_Eligibility.py")

st.markdown(
    f'<div class="sample-link-wrap"><a href="/Sample_Cases">{home_text("example")} →</a></div>'
    f'<div class="trust-row"><span>✓ {home_text("trust1")}</span>'
    f'<span>✓ {home_text("trust2")}</span><span>✓ {home_text("trust3")}</span></div>',
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
            f'<article class="step-card"><span class="step-num">{number}</span>'
            f'<h3>{title}</h3><p>{body}</p></article>',
            unsafe_allow_html=True,
        )

st.markdown(
    f'<div class="lender-strip"><span>{home_text("lender_caption")}</span>'
    '<strong>SBI</strong><strong>HDFC Bank</strong><strong>ICICI Bank</strong>'
    '<strong>Axis Bank</strong><strong>Bajaj Finance</strong><strong>Tata Capital</strong></div>',
    unsafe_allow_html=True,
)

st.info(t("model_warning"), icon="ℹ️")
footer()
