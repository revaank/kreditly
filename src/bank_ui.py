from __future__ import annotations

"""Accessible Streamlit rendering for published lender eligibility checks."""
import streamlit as st

from .bank_checker import check_all, count_meets, load_bank_rules
from .finance import format_inr
from .translations import t

STATUS_ICON = {"pass": "✅", "warn": "⚠️", "fail": "❌"}
STATUS_RANK = {"meets": 0, "close": 1, "limited": 2, "not_yet": 3}


def _translate_note(lender_id, rule_key, note, note_hi=None):
    from .translations import _request_language
    lang = _request_language.get()
    if lang is None:
        try:
            lang = st.session_state.get("language", "EN")
        except Exception:
            lang = "EN"
    if lang == "हिं" and note_hi:
        return note_hi
    return note or ""


def _employment(value):
    key = {"Salaried": "bank_salaried", "Self-employed": "bank_self_employed"}.get(value)
    return t(key) if key else str(value)


def _value_text(rule, result):
    key = rule["key"]
    value, requirement = rule["user_value"], rule["requirement"]
    if key == "employment_types_allowed":
        actual = _employment(value)
        required = ", ".join(_employment(item) for item in requirement)
    elif key == "min_age":
        actual, required = f"{value:g} {t('bank_years')}", f"≥ {requirement} {t('bank_years')}"
    elif key == "max_age":
        actual = f"{value:.0f} {t('bank_years')}"
        required = f"≤ {requirement['value']} {t('bank_years')}"
        if requirement["at_maturity"]:
            required += f" {t('bank_age_at_maturity')}"
    elif key == "min_monthly_income":
        actual = format_inr(value)
        required = f"≥ {format_inr(requirement['value'])}"
        if requirement.get("existing_customer_value") is not None:
            required += f" · {format_inr(requirement['existing_customer_value'])} {t('bank_existing_customer')}"
    elif key == "min_current_job_years":
        actual = f"{value:g} {t('bank_years')}"
        required = f"≥ {requirement} {t('bank_years')}"
    elif key == "min_cibil":
        actual = str(value)
        required = f"≥ {requirement}"
    elif key == "max_foir":
        actual = f"{value:.1f}%"
        required = f"≤ {requirement}%"
    elif key in {"min_loan", "max_loan"}:
        actual = format_inr(value)
        operator = "≥" if key == "min_loan" else "≤"
        required = f"{operator} {format_inr(requirement)}"
    elif key == "max_tenure_months":
        actual = f"{value} {t('bank_months')}"
        required = f"≤ {requirement} {t('bank_months')}"
    elif key == "typical_foir":
        actual = f"{value:.1f}%"
        required = f"≤ {requirement['value']}%"
    else:
        actual, required = str(value), str(requirement)
    return t("bank_rule_comparison", user=actual, requirement=required)


def aggregate_next_steps(results: list[dict]) -> list[str]:
    """Aggregate all close and failed criteria across lenders into a single de-duplicated checklist."""
    all_fixes = []
    for lender in sorted(results, key=lambda item: STATUS_RANK.get(item.get("status"), 3)):
        if lender.get("status") in ("close", "not_yet"):
            for fix in lender.get("fixes", []):
                if fix and fix not in all_fixes:
                    all_fixes.append(fix)
    return all_fixes


def render_bank_results(user: dict, compact: bool = False):
    """Render six sorted lender cards or a compact live what-if count."""
    try:
        rules = load_bank_rules()
        results = check_all(user, rules)
    except Exception:
        st.error(t("bank_error"))
        return None

    total = len(results)
    met = count_meets(results)
    if compact:
        st.caption(t("bank_compact_count", count=met, total=total))
        return results

    st.subheader(t("bank_section"))
    rules_meta = load_bank_rules()
    disclaimer_text = rules_meta.get("disclaimer_hi") if st.session_state.get("language") == "हिं" and rules_meta.get("disclaimer_hi") else rules_meta.get("disclaimer", t("bank_disclaimer"))
    st.info(disclaimer_text)
    st.caption(t("bank_last_checked", date=rules.get("last_checked", "")))
    st.caption(t("bank_reliability_legend"))
    st.write(t("bank_summary", count=met, total=total))

    overall_fixes = aggregate_next_steps(results)
    if overall_fixes:
        with st.container(border=True):
            st.markdown(f"**{t('bank_fixes')}**")
            for fix in overall_fixes:
                st.markdown(f"- {fix}")

    for lender in sorted(results, key=lambda item: STATUS_RANK[item["status"]]):
        with st.container(border=True):
            col_name, col_status = st.columns([3, 2], vertical_alignment="center")
            with col_name:
                st.markdown(f"### {lender['name']}")
                badge_key = "bank_type_nbfc" if lender["type"] == "NBFC" else "bank_type_bank"
                st.caption(f"{t(badge_key)} · {lender['product']}")
            with col_status:
                status_key = f"bank_status_{lender['status']}"
                st.markdown(
                    f'<span class="bank-status {lender["status"]}">{t(status_key)}</span>',
                    unsafe_allow_html=True,
                )
            if lender.get("interest_rate_from") is not None:
                st.markdown(t("bank_interest_from", rate=lender["interest_rate_from"]))
                rate_rule = lender["interest_rate_rule"]
                rate_reliability = "bank_official" if rate_rule.get("reliability") == "official" else "bank_typical"
                st.caption(t(rate_reliability))
                note = _translate_note(lender["id"], "interest_rate_from", lender["interest_rate_rule"].get("note"), lender["interest_rate_rule"].get("note_hi"))
                if note:
                    st.caption(note)
                if rate_rule.get("source"):
                    st.markdown(f"[{t('bank_view_source')}]({rate_rule['source']})")
                    if rate_rule.get("needs_review"):
                        st.caption(t("bank_source_review"))

            for row in lender["rules"]:
                cols = st.columns([3, 6, 1], vertical_alignment="center")
                with cols[0]:
                    st.markdown(f"{STATUS_ICON[row['status']]} **{t('bank_rule_' + row['key'])}**")
                with cols[1]:
                    st.write(_value_text(row, lender))
                with cols[2]:
                    reliability_key = "bank_official" if row.get("reliability") == "official" else "bank_typical"
                    st.caption(t(reliability_key))
                if row.get("message_key"):
                    st.caption(t(row["message_key"], **row.get("message_values", {})))
                note = _translate_note(lender["id"], row["key"], row.get("note"), row.get("note_hi"))
                if note:
                    st.caption(f"{t('bank_note_label')}: {note}")
                if row.get("source"):
                    st.markdown(f"[{t('bank_view_source')}]({row['source']})")
                    if row.get("needs_review"):
                        st.caption(t("bank_source_review"))

            if lender["fixes"]:
                st.markdown(f"**{t('bank_fixes')}**")
                for fix in lender["fixes"]:
                    st.markdown(f"- {fix}")
            if lender.get("official_page"):
                st.markdown(f"[{t('lender_information_page')}]({lender['official_page']})")

    st.warning(t("bank_footer"), icon="⚠️")
    return results


def get_lender_key_reason(lender: dict) -> str:
    """Return the single most critical reason for the lender's status."""
    status = lender.get("status")
    if status == "meets":
        return t("lender_all_met")
    for rule in lender.get("rules", []):
        if status == "not_yet" and rule.get("status") == "fail":
            return f"{t('bank_rule_' + rule['key'])} ({_value_text(rule, lender)})"
        elif status == "close" and rule.get("status") == "warn":
            return f"{t('bank_rule_' + rule['key'])} ({_value_text(rule, lender)})"
    fixes = lender.get("fixes", [])
    if fixes:
        return fixes[0]
    return t(f"bank_status_{status}")


def render_lender_cards(results: list[dict]):
    """Render 15 lenders as clean rows with summary header and expand/collapse, matching design tokens."""
    rules_meta = load_bank_rules()
    last_checked = rules_meta.get("last_checked", "")

    # Count breakdown
    meets_c = sum(1 for x in results if x.get("status") == "meets")
    close_c = sum(1 for x in results if x.get("status") == "close")
    limited_c = sum(1 for x in results if x.get("status") == "limited")
    not_yet_c = sum(1 for x in results if x.get("status") == "not_yet")

    col_h_title, col_h_sum = st.columns([1, 1], vertical_alignment="center")
    with col_h_title:
        st.markdown('<div class="wizard-card-title" style="font-size: 24px !important; margin: 0 !important;">Lenders</div>', unsafe_allow_html=True)
    with col_h_sum:
        st.markdown(
            f'<div style="text-align: right; font-size: 13px; color: var(--muted);">'
            f'<strong style="color: #1F7A4D;">{meets_c} meet</strong> · '
            f'<span>{close_c} close</span> · '
            f'<span>{limited_c + not_yet_c} few rules published</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)

    sorted_results = sorted(results, key=lambda item: STATUS_RANK.get(item.get("status"), 3))

    show_all_key = "show_all_lenders_expanded"
    if show_all_key not in st.session_state:
        st.session_state[show_all_key] = False

    displayed_results = sorted_results if st.session_state[show_all_key] else sorted_results[:5]

    status_dot_color = {
        "meets": "#1F7A4D",
        "close": "#B7791F",
        "limited": "#9CA3AF",
        "not_yet": "#B5523B",
    }

    cibil_idx = st.session_state.get("profile", {}).get("cibil_index", 1)
    if cibil_idx == 0:
        rate_hint = t("rate_hint_excellent")
    elif cibil_idx == 1:
        rate_hint = t("rate_hint_good")
    elif cibil_idx == 2:
        rate_hint = t("rate_hint_average")
    elif cibil_idx == 3:
        rate_hint = t("rate_hint_low")
    else:
        rate_hint = t("rate_hint_none")

    for lender in displayed_results:
        dot_color = status_dot_color.get(lender.get("status"), "#9CA3AF")
        rate_from = lender.get("interest_rate_from")
        rate_to = lender.get("interest_rate_to")
        if rate_from is not None:
            rate_str = f"{rate_from:.1f}%–{rate_to:.1f}%" if rate_to is not None else f"from {rate_from:.1f}%"
        else:
            rate_str = t("bank_interest_not_published")

        key_reason = get_lender_key_reason(lender)

        with st.container(border=True):
            col_dot, col_info, col_rate = st.columns([0.4, 6.6, 3.0], vertical_alignment="center")
            with col_dot:
                st.markdown(
                    f'<div style="width: 10px; height: 10px; border-radius: 50%; background: {dot_color}; margin-top: 4px;"></div>',
                    unsafe_allow_html=True,
                )
            with col_info:
                badge_type = t("bank_type_nbfc") if lender.get("type") == "NBFC" else t("bank_type_bank")
                st.markdown(
                    f'<div style="line-height: 1.3;">'
                    f'<span style="font-weight: 700; font-size: 15px; color: var(--ink); margin-right: 8px;">{lender["name"]}</span>'
                    f'<span style="font-size: 12px; color: var(--muted);">{badge_type}</span>'
                    f'<div style="font-size: 13px; color: var(--muted); margin-top: 2px;">{key_reason}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with col_rate:
                st.markdown(
                    f'<div style="text-align: right; line-height: 1.3;">'
                    f'<div style="font-weight: 600; font-size: 14px; color: var(--ink);">{rate_str}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            with st.expander(t("see_all_rules")):
                if lender.get("requires_salary_account"):
                    sal_note = lender.get("salary_account_note_hi") if st.session_state.get("language") == "हिं" and lender.get("salary_account_note_hi") else lender.get("salary_account_note")
                    if sal_note:
                        st.markdown(f'<div style="font-size:12px;color:#854D0E;background:#FEF3C7;padding:6px 10px;border-radius:8px;margin-bottom:8px;">ℹ️ {sal_note}</div>', unsafe_allow_html=True)

                fee = lender.get("processing_fee")
                if fee and isinstance(fee, dict):
                    fee_text = fee.get("text_hi") if st.session_state.get("language") == "हिं" and fee.get("text_hi") else fee.get("text")
                    if fee_text:
                        st.markdown(f'<div style="font-size:13px;color:#4A554F;margin-bottom:8px;"><b>{t("bank_processing_fee")}:</b> {fee_text}</div>', unsafe_allow_html=True)

                st.caption(f"💡 {rate_hint}")

                for row in lender["rules"]:
                    cols = st.columns([3, 6, 1], vertical_alignment="center")
                    with cols[0]:
                        st.markdown(f"{STATUS_ICON[row['status']]} **{t('bank_rule_' + row['key'])}**")
                    with cols[1]:
                        st.write(_value_text(row, lender))
                    with cols[2]:
                        reliability_key = "bank_official" if row.get("reliability") == "official" else "bank_typical"
                        st.caption(t(reliability_key))
                    if row.get("message_key"):
                        st.caption(t(row["message_key"], **row.get("message_values", {})))
                    note = _translate_note(lender["id"], row["key"], row.get("note"), row.get("note_hi"))
                    if note:
                        st.caption(f"{t('bank_note_label')}: {note}")

                if lender.get("official_page"):
                    st.markdown(f'<a href="{lender["official_page"]}" target="_blank" rel="noopener noreferrer" style="color:var(--ink);text-decoration:underline;">{t("visit_official_page")} ↗</a>', unsafe_allow_html=True)
                if last_checked:
                    st.caption(t("bank_checked_date", date=last_checked))

    if len(sorted_results) > 5:
        if not st.session_state[show_all_key]:
            if st.button(f"{t('show_all_lenders')} ({len(sorted_results)}) ↓", use_container_width=True, key="btn_show_more_lenders"):
                st.session_state[show_all_key] = True
                st.rerun()
        else:
            if st.button(t("show_less_lenders"), use_container_width=True, key="btn_show_less_lenders"):
                st.session_state[show_all_key] = False
                st.rerun()

