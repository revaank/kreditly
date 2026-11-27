"""Borrower Guide: CIBIL basics, searchable glossary, and document checklist."""
from __future__ import annotations

import streamlit as st
from src.translations import t
from src.ui import chip_selector, footer, header, page_setup, section_title

page_setup()
header("guide")
section_title(t("guide_title"), t("guide_subtitle"))

tab_cibil, tab_glossary, tab_docs = st.tabs([
    t("guide_tab_cibil"),
    t("guide_tab_glossary"),
    t("guide_tab_docs"),
])

# ==============================================================================
# TAB A — CIBIL basics
# ==============================================================================
with tab_cibil:
    cibil_sections = [
        ("cibil_what_title", "cibil_what_body", "📊"),
        ("cibil_bands_title", "cibil_bands_body", "🎯"),
        ("cibil_raises_title", "cibil_raises_body", "📈"),
        ("cibil_lowers_title", "cibil_lowers_body", "📉"),
        ("cibil_free_title", "cibil_free_body", "🎁"),
        ("cibil_time_title", "cibil_time_body", "⏱️"),
    ]

    for title_k, body_k, icon in cibil_sections:
        with st.container(border=True):
            st.markdown(f"#### {icon} {t(title_k)}")
            st.markdown(f'<p style="font-size:14px;color:#35443A;line-height:1.6;margin:0;">{t(body_k)}</p>', unsafe_allow_html=True)


# ==============================================================================
# TAB B — Words you'll see (Glossary)
# ==============================================================================
with tab_glossary:
    glossary_items = [
        ("gloss_emi", "gloss_emi_desc"),
        ("gloss_cibil", "gloss_cibil_desc"),
        ("gloss_foir", "gloss_foir_desc"),
        ("gloss_proc_fee", "gloss_proc_fee_desc"),
        ("gloss_gst", "gloss_gst_desc"),
        ("gloss_apr", "gloss_apr_desc"),
        ("gloss_kfs", "gloss_kfs_desc"),
        ("gloss_tenure", "gloss_tenure_desc"),
        ("gloss_prepay", "gloss_prepay_desc"),
        ("gloss_rate_type", "gloss_rate_type_desc"),
        ("gloss_coapplicant", "gloss_coapplicant_desc"),
        ("gloss_salary_acc", "gloss_salary_acc_desc"),
        ("gloss_hard_enquiry", "gloss_hard_enquiry_desc"),
        ("gloss_cooling_off", "gloss_cooling_off_desc"),
        ("gloss_nbfc", "gloss_nbfc_desc"),
    ]

    search_query = st.text_input(
        "🔍",
        placeholder=t("glossary_search_placeholder"),
        key="txt_glossary_search",
        label_visibility="collapsed",
    ).strip().lower()

    filtered = []
    for term_k, desc_k in glossary_items:
        term_text = t(term_k)
        desc_text = t(desc_k)
        if not search_query or search_query in term_text.lower() or search_query in desc_text.lower():
            filtered.append((term_text, desc_text))

    if not filtered:
        st.info(t("glossary_no_match"))
    else:
        for term_text, desc_text in filtered:
            with st.container(border=True):
                st.markdown(f"**{term_text}**")
                st.markdown(f'<p style="font-size:14px;color:#4A554F;line-height:1.5;margin:4px 0 0;">{desc_text}</p>', unsafe_allow_html=True)


# ==============================================================================
# TAB C — Documents checklist
# ==============================================================================
with tab_docs:
    emp_choice = chip_selector(
        t("employment"),
        [t("docs_salaried"), t("docs_self_employed")],
        t("docs_salaried"),
        key="chip_docs_emp",
    )

    salaried_keys = [
        "doc_sal_pan",
        "doc_sal_aadhaar",
        "doc_sal_slips",
        "doc_sal_bank",
        "doc_sal_form16",
        "doc_sal_job_proof",
        "doc_sal_photo",
    ]

    self_emp_keys = [
        "doc_se_pan",
        "doc_se_aadhaar",
        "doc_se_itr",
        "doc_se_bank",
        "doc_se_biz_proof",
        "doc_se_pl_balance",
        "doc_se_office_proof",
    ]

    is_salaried = (emp_choice == t("docs_salaried"))
    active_keys = salaried_keys if is_salaried else self_emp_keys
    prefix = "doc_chk_sal" if is_salaried else "doc_chk_se"

    checked_count = 0
    with st.container(border=True):
        for idx, k in enumerate(active_keys):
            item_key = f"{prefix}_{idx}"
            checked = st.checkbox(t(k), value=bool(st.session_state.get(item_key, False)), key=item_key)
            if checked:
                checked_count += 1

    total_docs = len(active_keys)
    progress_val = checked_count / total_docs
    st.progress(progress_val)
    st.caption(f"📋 **{t('docs_ready_count', ready=checked_count, total=total_docs)}**")
    st.info(f"ℹ️ {t('docs_note')}")

footer()
