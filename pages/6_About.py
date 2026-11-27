"""About Kreditly: mission, analytical methodology, privacy policy, and limits."""
from __future__ import annotations

import streamlit as st
from src.bank_checker import load_bank_rules
from src.translations import t
from src.ui import footer, header, page_intro, page_setup

page_setup()
header("about")

st.markdown('<div class="results-outer-wrapper">', unsafe_allow_html=True)
page_intro("ABOUT", t("about_title"), t("about_subtitle"))

rules_meta = load_bank_rules()
last_checked = rules_meta.get("last_checked", "November 2026")

# 1. 2-column grid for sections
col_a1, col_a2 = st.columns(2)
with col_a1:
    with st.container(border=True):
        st.markdown(f'<div class="wizard-card-title" style="font-size:18px !important;margin-bottom:8px !important;">🛡️ {t("about_what_title")}</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:14px;color:var(--muted);line-height:1.6;margin:0;">{t("about_what_body")}</p>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f'<div class="wizard-card-title" style="font-size:18px !important;margin-bottom:8px !important;">🔒 {t("about_privacy_title")}</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:14px;color:var(--muted);line-height:1.6;margin:0;">{t("about_privacy_body")}</p>', unsafe_allow_html=True)

with col_a2:
    with st.container(border=True):
        st.markdown(f'<div class="wizard-card-title" style="font-size:18px !important;margin-bottom:8px !important;">⚠️ {t("about_limits_title")}</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:14px;color:var(--muted);line-height:1.6;margin:0;">{t("about_limits_body")}</p>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f'<div class="wizard-card-title" style="font-size:18px !important;margin-bottom:8px !important;">👩‍💻 {t("about_who_title")}</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:14px;color:var(--muted);line-height:1.6;margin:0 0 12px 0;">{t("about_who_body")}</p>', unsafe_allow_html=True)
        st.link_button(f"{t('about_feedback_link')} ↗", "https://github.com/revaank/kreditly/issues/new", use_container_width=True)

# 2. How it works (Full-width card with 4 numbered rows)
with st.container(border=True):
    st.markdown(f'<div class="wizard-card-title" style="font-size:20px !important;margin-bottom:12px !important;">⚙️ {t("about_how_title")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:14px;color:var(--muted);line-height:1.6;margin-bottom:14px;">{t("about_how_body", last_checked=last_checked)}</div>', unsafe_allow_html=True)
    
    col_btn_m, _ = st.columns([1.5, 2])
    with col_btn_m:
        try:
            st.page_link("pages/3_Model_Insights.py", label=t("about_insights_link"), icon="📊")
        except Exception:
            st.markdown(f'<a href="/Model_Insights" style="color:var(--ink);font-weight:600;text-decoration:none;">📊 {t("about_insights_link")}</a>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
footer()
