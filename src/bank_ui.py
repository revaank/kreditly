from __future__ import annotations

"""Accessible Streamlit rendering for published lender eligibility checks."""
import streamlit as st

from .bank_checker import check_all, count_meets, load_bank_rules
from .finance import format_inr
from .translations import t

STATUS_ICON = {"pass": "✅", "warn": "⚠️", "fail": "❌"}
STATUS_RANK = {"meets": 0, "close": 1, "not_yet": 2}


def _translate_note(lender_id, rule_key, note):
    if not note:
        return ""
    key = f"bank_note_{lender_id}_{rule_key}"
    translated = t(key)
    return note if translated == key else translated


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
    st.info(t("bank_disclaimer"))
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
                note = _translate_note(lender["id"], "interest_rate_from", lender["interest_rate_rule"].get("note"))
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
                note = _translate_note(lender["id"], row["key"], row.get("note"))
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
    """Render six sorted lender cards with badge, key reason and full criteria in an expander."""
    for lender in sorted(results, key=lambda item: STATUS_RANK[item["status"]]):
        with st.container(border=True):
            col_name, col_status = st.columns([3, 2], vertical_alignment="center")
            with col_name:
                st.markdown(f"### {lender['name']}")
                badge_key = "bank_type_nbfc" if lender["type"] == "NBFC" else "bank_type_bank"
                st.caption(f"{t(badge_key)} · {lender['product']}")
            with col_status:
                status = lender["status"]
                badge_text = t("qualify_badge_meets") if status == "meets" else (t("qualify_badge_close") if status == "close" else t("qualify_badge_not_yet"))
                st.markdown(
                    f'<span class="bank-status {status}">{badge_text}</span>',
                    unsafe_allow_html=True,
                )
            key_reason = get_lender_key_reason(lender)
            st.markdown(f'<p style="font-size:14px;color:#34433A;margin:8px 0 10px;"><b>{t("key_reason")}:</b> {key_reason}</p>', unsafe_allow_html=True)
            with st.expander(t("see_all_rules")):
                if lender.get("interest_rate_from") is not None:
                    st.markdown(t("bank_interest_from", rate=lender["interest_rate_from"]))
                    rate_rule = lender["interest_rate_rule"]
                    rate_reliability = "bank_official" if rate_rule.get("reliability") == "official" else "bank_typical"
                    st.caption(t(rate_reliability))
                    note = _translate_note(lender["id"], "interest_rate_from", lender["interest_rate_rule"].get("note"))
                    if note:
                        st.caption(note)
                    if rate_rule.get("source"):
                        st.markdown(f"[{t('bank_view_source')}]({rate_rule['source']})")
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
                    note = _translate_note(lender["id"], row["key"], row.get("note"))
                    if note:
                        st.caption(f"{t('bank_note_label')}: {note}")
                    if row.get("source"):
                        st.markdown(f"[{t('bank_view_source')}]({row['source']})")
                if lender.get("official_page"):
                    st.markdown(f"[{t('lender_information_page')}]({lender['official_page']})")

