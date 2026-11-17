"""Kreditly's home page for an educational historical-model demonstration."""
import streamlit as st
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


page_setup()
header("home")

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
    st.markdown(
        f'<section class="sample-result"><div class="sample-top"><span>{home_text("sample")}</span>'
        f'<span class="sample-badge">{t("readiness_needs_work")}</span></div>'
        f'<div class="sample-title">{t("readiness_needs_work")}</div>'
        f'<div class="sample-meter"><span></span></div>'
        f'<div class="sample-stats"><div><small>{home_text("lenders")}</small><strong>5 / 6</strong></div>'
        f'<div><small>{t("monthly_emi")}</small><strong>₹9,822</strong></div></div>'
        f'<div class="sample-fix"><small>{home_text("fix")}</small><p>{home_text("sample_fix")}</p></div></section>',
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
