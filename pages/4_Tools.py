"""Borrower tools: offer comparison, early prepayment, loan app safety, and rejection help."""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src.finance import format_inr
from src.tools import SAFETY_QUESTIONS, app_safety_result, compare_offer, prepay
from src.translations import t
from src.ui import chip_selector, footer, header, page_setup, section_title

page_setup()
header("tools")
section_title(t("tools_title"), t("tools_subtitle"))

tab_compare, tab_prepay, tab_safety, tab_rejection = st.tabs([
    t("tools_tab_compare"),
    t("tools_tab_prepay"),
    t("tools_tab_safety"),
    t("tools_tab_rejection"),
])

# ==============================================================================
# TAB A — Compare offers
# ==============================================================================
with tab_compare:
    profile = st.session_state.get("profile", {})
    def_amount = float(profile.get("loan_amount", 300000))
    def_tenure = int(profile.get("tenure_months", 36))
    def_rate = float(profile.get("rate", 11.0))

    add_third = st.checkbox(t("add_third_offer"), key="chk_add_offer3")
    num_offers = 3 if add_third else 2
    cols = st.columns(num_offers)

    offers_data = []
    defaults = [
        {"name": "Offer A", "amt": def_amount, "rate": def_rate, "tenure": def_tenure, "feetype": t("fee_toggle_pct"), "feepct": 2.0, "feeamt": 6000.0, "other": 0.0},
        {"name": "Offer B", "amt": def_amount, "rate": max(1.0, def_rate + 0.5), "tenure": def_tenure, "feetype": t("fee_toggle_pct"), "feepct": 0.5, "feeamt": 1500.0, "other": 0.0},
        {"name": "Offer C", "amt": def_amount, "rate": max(1.0, def_rate - 0.25), "tenure": def_tenure, "feetype": t("fee_toggle_amt"), "feepct": 1.0, "feeamt": 2500.0, "other": 500.0},
    ]

    for idx, col in enumerate(cols):
        i = idx + 1
        d = defaults[idx]
        with col:
            with st.container(border=True):
                st.markdown(f"#### {t('offer_label', n=i)}")
                name_in = st.text_input(
                    t("offer_name"),
                    value=d["name"],
                    placeholder=t("offer_lender_placeholder"),
                    key=f"offer_name_{i}",
                )
                amt_in = st.number_input(
                    f"{t('loan_amount')} (₹)",
                    min_value=10000,
                    max_value=10000000,
                    value=int(d["amt"]),
                    step=25000,
                    key=f"offer_amt_{i}",
                )
                rate_in = st.number_input(
                    t("rate"),
                    min_value=1.0,
                    max_value=50.0,
                    value=float(d["rate"]),
                    step=0.25,
                    key=f"offer_rate_{i}",
                )
                tenure_in = st.number_input(
                    f"{t('tenure')} ({t('months')})",
                    min_value=6,
                    max_value=84,
                    value=int(d["tenure"]),
                    step=6,
                    key=f"offer_tenure_{i}",
                )
                fee_mode = st.radio(
                    t("processing_fee"),
                    [t("fee_toggle_pct"), t("fee_toggle_amt")],
                    index=0 if d["feetype"] == t("fee_toggle_pct") else 1,
                    horizontal=True,
                    key=f"offer_feemode_{i}",
                )
                if fee_mode == t("fee_toggle_pct"):
                    feepct_val = st.number_input(
                        f"{t('processing_fee')} (%)",
                        min_value=0.0,
                        max_value=10.0,
                        value=float(d["feepct"]),
                        step=0.25,
                        key=f"offer_feepct_{i}",
                    )
                    feeamt_val = None
                else:
                    feeamt_val = st.number_input(
                        f"{t('processing_fee')} (₹)",
                        min_value=0.0,
                        max_value=200000.0,
                        value=float(d["feeamt"]),
                        step=500.0,
                        key=f"offer_feeamt_{i}",
                    )
                    feepct_val = None

                other_in = st.number_input(
                    t("other_charges"),
                    min_value=0.0,
                    max_value=100000.0,
                    value=float(d["other"]),
                    step=500.0,
                    key=f"offer_other_{i}",
                )

                calc = compare_offer(
                    amt_in,
                    rate_in,
                    tenure_in,
                    fee_pct=feepct_val,
                    fee_amt=feeamt_val,
                    other=other_in,
                )
                display_name = name_in.strip() if name_in.strip() else t("offer_label", n=i)
                offers_data.append({
                    "id": i,
                    "name": display_name,
                    "amount": amt_in,
                    "rate": rate_in,
                    "tenure": tenure_in,
                    "calc": calc,
                })

    # Find cheapest offer
    cheapest = min(offers_data, key=lambda x: x["calc"]["total_cost"])

    st.markdown("---")

    # Comparison Table
    table_header = f"| {t('summary')} | " + " | ".join([o["name"] for o in offers_data]) + " |"
    table_sep = "| :--- | " + " | ".join([":---:" for _ in offers_data]) + " |"

    def format_row(title: str, values: list[str]) -> str:
        return f"| **{title}** | " + " | ".join(values) + " |"

    emi_vals = [format_inr(o["calc"]["emi"]) for o in offers_data]
    interest_vals = [format_inr(o["calc"]["total_interest"]) for o in offers_data]
    fee_vals = [format_inr(o["calc"]["fees"]) for o in offers_data]

    cost_vals = []
    for o in offers_data:
        val = format_inr(o["calc"]["total_cost"])
        if o["id"] == cheapest["id"]:
            val += f'<br><span style="display:inline-block;background:#ECFCCB;color:#365314;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:700;">{t("cheapest_badge")}</span>'
        cost_vals.append(val)

    recv_vals = [format_inr(o["calc"]["money_in_hand"]) for o in offers_data]
    apr_vals = [f"**{o['calc']['effective_annual_rate']:.2f}%**" for o in offers_data]

    table_md = "\n".join([
        table_header,
        table_sep,
        format_row(t("compare_row_emi"), emi_vals),
        format_row(t("compare_row_interest"), interest_vals),
        format_row(t("compare_row_fees"), fee_vals),
        format_row(t("compare_row_total_cost"), cost_vals),
        format_row(t("compare_row_received"), recv_vals),
        format_row(t("compare_row_effective_rate"), apr_vals),
    ])

    st.markdown(table_md, unsafe_allow_html=True)

    # Dynamic plain sentence comparing cheapest vs second cheapest
    sorted_offers = sorted(offers_data, key=lambda x: x["calc"]["total_cost"])
    c_off = sorted_offers[0]
    r_off = sorted_offers[1]
    diff = r_off["calc"]["total_cost"] - c_off["calc"]["total_cost"]

    if diff > 0:
        if c_off["rate"] > r_off["rate"]:
            rate_comp = t("rate_comp_higher")
            fee_comp = t("fee_comp_lower")
            summary_sentence = t("compare_summary_sentence", cheapest=c_off["name"], diff=format_inr(diff), rate_comp=rate_comp, fee_comp=fee_comp)
        elif c_off["rate"] < r_off["rate"]:
            rate_comp = t("rate_comp_lower")
            fee_comp = t("fee_comp_lower") if c_off["calc"]["fees"] <= r_off["calc"]["fees"] else t("fee_comp_higher")
            summary_sentence = t("compare_summary_sentence", cheapest=c_off["name"], diff=format_inr(diff), rate_comp=rate_comp, fee_comp=fee_comp)
        else:
            summary_sentence = t("compare_summary_cheapest_general", cheapest=c_off["name"], diff=format_inr(diff))
    else:
        summary_sentence = t("compare_summary_cheapest_general", cheapest=c_off["name"], diff=format_inr(0))

    st.markdown(f'<p style="font-size:15px;color:#1F7A4D;font-weight:600;margin:16px 0 10px;">{summary_sentence}</p>', unsafe_allow_html=True)
    st.info(f"💡 **Key Fact Statement (KFS):** {t('kfs_tip_box')}")


# ==============================================================================
# TAB B — Prepay early
# ==============================================================================
with tab_prepay:
    profile = st.session_state.get("profile", {})
    def_loan = float(profile.get("loan_amount", 300000))
    def_rate = float(profile.get("rate", 11.0))
    def_tenure = int(profile.get("tenure_months", 36))

    c1, c2, c3 = st.columns(3)
    with c1:
        p_amount = st.number_input(f"{t('loan_amount')} (₹)", min_value=10000, max_value=10000000, value=int(def_loan), step=25000, key="prepay_amt")
    with c2:
        p_rate = st.number_input(t("rate"), min_value=1.0, max_value=50.0, value=float(def_rate), step=0.25, key="prepay_rate")
    with c3:
        p_months = st.number_input(f"{t('tenure')} ({t('months')})", min_value=6, max_value=84, value=int(def_tenure), step=6, key="prepay_tenure")

    c4, c5, c6 = st.columns(3)
    with c4:
        p_after = st.slider(t("prepay_after_month"), min_value=1, max_value=max(2, p_months - 1), value=min(12, max(1, p_months - 1)), key="prepay_after")
    with c5:
        p_lump = st.number_input(t("prepay_lump_sum"), min_value=0, max_value=int(p_amount), value=min(50000, int(p_amount)), step=5000, key="prepay_lump")
    with c6:
        p_charge = st.number_input(t("prepay_charge_pct"), min_value=0.0, max_value=10.0, value=0.0, step=0.5, key="prepay_charge")

    p_mode = st.radio(t("prepay_mode_label"), [t("prepay_mode_tenure"), t("prepay_mode_emi")], horizontal=True, key="prepay_mode_radio")
    norm_mode = "tenure" if p_mode == t("prepay_mode_tenure") else "emi"

    res_p = prepay(p_amount, p_rate, p_months, p_after, p_lump, charge_pct=p_charge, mode=norm_mode)

    st.caption(f"{t('prepay_current_balance')}: **{format_inr(res_p['outstanding_balance'])}**")
    if res_p["is_foreclosure"]:
        st.success(f"🎉 **{t('prepay_foreclosure_badge')}**")

    # 3 big numbers + time/EMI impact
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(t("prepay_stat_interest_saved"), format_inr(res_p["interest_saved"]))
    m2.metric(t("prepay_stat_charge_paid"), format_inr(res_p["charge_paid"]))
    m3.metric(t("prepay_stat_net_saving"), format_inr(res_p["net_saving"]))
    if norm_mode == "tenure":
        m4.metric(t("prepay_stat_months_saved"), f"{res_p['months_saved']} {t('months')}")
    else:
        m4.metric(t("prepay_stat_new_emi"), format_inr(res_p["new_emi"]))

    if res_p["net_saving"] <= 0 and p_lump > 0 and p_charge > 0:
        st.warning(t("prepay_no_saving_note"))

    # Line chart of balance over time
    fig_prepay = go.Figure()
    x_axis = list(range(len(res_p["original_balances"])))
    fig_prepay.add_trace(go.Scatter(
        x=x_axis,
        y=res_p["original_balances"],
        name=t("prepay_chart_original"),
        line=dict(color="#9CA3AF", dash="dash", width=2),
    ))
    fig_prepay.add_trace(go.Scatter(
        x=x_axis,
        y=res_p["prepay_balances"],
        name=t("prepay_chart_prepaid"),
        line=dict(color="#15803D", width=3),
    ))
    fig_prepay.update_layout(
        title=t("prepay_chart_title"),
        xaxis_title=t("months"),
        yaxis_title="₹",
        height=320,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_prepay, use_container_width=True, config={"displayModeBar": False})

    st.caption(t("prepay_rbi_rule_note"))


# ==============================================================================
# TAB C — Is this loan app safe?
# ==============================================================================
with tab_safety:
    user_answers = []

    for idx, q_info in enumerate(SAFETY_QUESTIONS):
        i = idx + 1
        ans = st.radio(
            t(q_info["key"]),
            [t("ans_yes"), t("ans_no"), t("ans_not_sure")],
            index=2,
            horizontal=True,
            key=f"safety_q_{i}",
        )
        user_answers.append(ans)

    st.markdown("---")

    res_safety = app_safety_result(user_answers)
    status = res_safety["status"]

    if status == "red":
        st.error(f"🚨 **{t('safety_res_red', n=res_safety['red_flags'])}**")
    elif status == "amber":
        st.warning(f"⚠️ **{t('safety_res_amber')}**")
    elif status == "incomplete":
        st.warning(f"⚠️ **{t('safety_res_incomplete')}**")
    elif status == "unanswered":
        st.info(f"ℹ️ {t('safety_res_unanswered')}")
    elif status == "green":
        st.success(f"✅ **{t('safety_res_green')}**")

    with st.container(border=True):
        st.markdown(f"#### {t('safety_how_to_check')}")
        st.markdown(f"- 🏛️ [{t('safety_link_rbi_directory')}](https://www.rbi.org.in)")
        st.markdown(f"- ⚠️ [{t('safety_link_sachet')}](https://sachet.rbi.org.in)")
        st.markdown(f"- ⚖️ [{t('safety_link_cms')}](https://cms.rbi.org.in)")
        st.markdown(f"- 🚨 [{t('safety_link_cybercrime')}](https://cybercrime.gov.in)")

    st.caption(t("safety_facts_line"))


# ==============================================================================
# TAB D — I got rejected
# ==============================================================================
with tab_rejection:
    st.markdown(f"### {t('rej_title')}")

    reasons = [
        ("cibil", t("rej_reason_cibil")),
        ("foir", t("rej_reason_foir")),
        ("income", t("rej_reason_income")),
        ("job", t("rej_reason_job")),
        ("enquiries", t("rej_reason_enquiries")),
        ("age_emp", t("rej_reason_age_emp")),
        ("none", t("rej_reason_none")),
    ]
    reason_labels = [label for _, label in reasons]
    selected_label = chip_selector(t("rej_reason_q"), reason_labels, reason_labels[0], key="chip_rej_reason")
    selected_code = next(code for code, label in reasons if label == selected_label)

    applied_opts = ["0", "1", "2", "3+"]
    applied_val = chip_selector(t("rej_applied_q"), applied_opts, "0", key="chip_rej_applied")

    if applied_val in ("2", "3+"):
        st.warning(f"⚠️ {t('rej_enquiry_warning')}")

    with st.container(border=True):
        st.markdown(f"### {selected_label}")
        st.markdown(f"**{t('rej_card_meaning')}:** {t(f'rej_{selected_code}_meaning')}")
        st.markdown(f"**{t('rej_card_steps')}:**")
        st.markdown(f"1. {t(f'rej_{selected_code}_step1')}")
        st.markdown(f"2. {t(f'rej_{selected_code}_step2')}")
        st.markdown(f"3. {t(f'rej_{selected_code}_step3')}")
        st.markdown(f"⏱️ **{t('rej_card_wait')}:** {t(f'rej_{selected_code}_wait')}")

    if st.button(t("rej_btn_check"), type="primary", key="btn_rej_to_check"):
        st.switch_page("pages/1_Check_Eligibility.py")

footer()
