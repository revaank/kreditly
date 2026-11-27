"""About Kreditly: mission, analytical methodology, privacy policy, and limits."""
from __future__ import annotations

import streamlit as st
from src.bank_checker import load_bank_rules
from src.translations import t
from src.ui import footer, header, page_setup, section_title

page_setup()
header("about")
section_title(t("about_title"), t("about_subtitle"))

rules_meta = load_bank_rules()
last_checked = rules_meta.get("last_checked", "November 2026")

# 1. What Kreditly is
with st.container(border=True):
    st.markdown(f"### 🛡️ {t('about_what_title')}")
    st.markdown(f'<p style="font-size:15px;color:#35443A;line-height:1.6;">{t("about_what_body")}</p>', unsafe_allow_html=True)

# 2. How it works
with st.container(border=True):
    st.markdown(f"### ⚙️ {t('about_how_title')}")
    st.markdown(t("about_how_body", last_checked=last_checked))
    try:
        st.page_link("pages/3_Model_Insights.py", label=t("about_insights_link"), icon="📊")
    except Exception:
        st.markdown(f'<a href="/Model_Insights" style="color:#0C5A3E;font-weight:600;text-decoration:none;">📊 {t("about_insights_link")}</a>', unsafe_allow_html=True)

# 3. Privacy
with st.container(border=True):
    st.markdown(f"### 🔒 {t('about_privacy_title')}")
    st.markdown(f'<p style="font-size:15px;color:#35443A;line-height:1.6;">{t("about_privacy_body")}</p>', unsafe_allow_html=True)

# 4. Limits
with st.container(border=True):
    st.markdown(f"### ⚠️ {t('about_limits_title')}")
    st.markdown(f'<p style="font-size:15px;color:#35443A;line-height:1.6;">{t("about_limits_body")}</p>', unsafe_allow_html=True)

# 5. Who made it & Feedback
with st.container(border=True):
    st.markdown(f"### 👩‍💻 {t('about_who_title')}")
    st.markdown(f'<p style="font-size:15px;color:#35443A;line-height:1.6;">{t("about_who_body")}</p>', unsafe_allow_html=True)
    st.link_button(t("about_feedback_link"), "https://github.com/revaank/kreditly/issues/new")

footer()
