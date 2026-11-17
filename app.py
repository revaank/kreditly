"""Kreditly's home page for an educational historical-model demonstration."""
import streamlit as st
from src.translations import t
from src.ui import footer, header, page_setup, section_title


page_setup()
header("home")

hero, preview = st.columns([1.15, 0.85], gap="large", vertical_alignment="center")
with hero:
    st.markdown(
        f'<div class="hero-pill">{t("v2_pill")}</div>'
        f'<h1 class="home-title">{t("v2_title")}</h1>'
        f'<p class="hero-copy">{t("v2_subtext")}</p>',
        unsafe_allow_html=True,
    )
    primary, secondary = st.columns(2, gap="small")
    with primary:
        st.page_link("pages/1_Check_Eligibility.py", label=t("start_check"), icon=":material/arrow_forward:", use_container_width=True)
    with secondary:
        st.page_link("pages/2_Sample_Cases.py", label=t("v2_example"), use_container_width=True)
    st.markdown(
        f'<div class="trust-row"><span>✓ {t("v2_trust1")}</span>'
        f'<span>✓ {t("v2_trust2")}</span><span>✓ {t("v2_trust3")}</span></div>',
        unsafe_allow_html=True,
    )

with preview:
    st.markdown(
        f'<section class="sample-result"><div class="sample-top"><span>{t("v2_sample_label")}</span>'
        f'<span class="sample-badge">{t("readiness_needs_work")}</span></div>'
        f'<div class="sample-title">{t("readiness_needs_work")}</div>'
        f'<div class="sample-meter"><span></span></div>'
        f'<div class="sample-stats"><div><small>{t("v2_lenders_met")}</small><strong>5 / 6</strong></div>'
        f'<div><small>{t("monthly_emi")}</small><strong>₹9,822</strong></div></div>'
        f'<div class="sample-fix"><small>{t("v2_fix_label")}</small><p>{t("v2_sample_fix")}</p></div></section>',
        unsafe_allow_html=True,
    )

st.markdown(
    f'<div class="lender-strip"><span>{t("v2_lender_caption")}</span>'
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

st.markdown(f'<section class="feature-panel"><h2>{t("v2_features_title")}</h2><div class="feature-grid">'
            f'<article><span>01</span><h3>{t("v2_feature1")}</h3><p>{t("v2_feature1_body")}</p></article>'
            f'<article><span>02</span><h3>{t("v2_feature2")}</h3><p>{t("v2_feature2_body")}</p></article>'
            f'<article><span>03</span><h3>{t("v2_feature3")}</h3><p>{t("v2_feature3_body")}</p></article>'
            f'<article><span>04</span><h3>{t("v2_feature4")}</h3><p>{t("v2_feature4_body")}</p></article>'
            '</div></section>', unsafe_allow_html=True)

st.info(t("model_warning"), icon="ℹ️")
footer()
