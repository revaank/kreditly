"""Kreditly's home page for an educational historical-model demonstration."""
import streamlit as st
from src.translations import t
from src.ui import footer, header, page_setup, section_title

page_setup()
header("home")
st.warning(t("model_warning"))
st.markdown('<div class="hero">', unsafe_allow_html=True)
st.markdown(f'<div class="eyebrow">{t("eyebrow")}</div><h1>{t("headline")}</h1><p class="hero-copy">{t("subtext")}</p>', unsafe_allow_html=True)
c1, c2 = st.columns([1, 1])
with c1: st.page_link("pages/1_Check_Eligibility.py", label=t("start_check"), icon="✅", use_container_width=True)
with c2: st.page_link("pages/2_Sample_Cases.py", label=t("sample_link"), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
st.write("")
for col, title, body, icon in zip(st.columns(3), [t("feature1"), t("feature2"), t("feature3")], [t("feature1_body"), t("feature2_body"), t("feature3_body")], ["⚡", "◉", "↗"]):
    with col: st.markdown(f'<div class="feature-card"><span class="feature-icon">{icon}</span><h3>{title}</h3><p>{body}</p></div>', unsafe_allow_html=True)
section_title(t("how_title"))
for idx, (col, title, body) in enumerate(zip(st.columns(3), [t("step1"), t("step2"), t("step3")], [t("step1_body"), t("step2_body"), t("step3_body")]), 1):
    with col: st.markdown(f'<div class="step-card"><span class="step-num">0{idx}</span><h3>{title}</h3><p>{body}</p></div>', unsafe_allow_html=True)
st.info(t("privacy_note"), icon="🔒")
footer()
