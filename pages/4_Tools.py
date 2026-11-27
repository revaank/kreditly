"""Borrower tools: offer comparison, early prepayment, loan app safety, and rejection help."""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from src.finance import format_inr
from src.tools import SAFETY_QUESTIONS, app_safety_result, compare_offer, prepay
from src.translations import t
from src.ui import chip_selector, footer, header, page_intro, page_setup, render_feedback

page_setup()
header("tools")

st.markdown('<div class="results-outer-wrapper">', unsafe_allow_html=True)
page_intro(t("tools_eyebrow") if "tools_eyebrow" in t.__globals__["EN"] else "TOOLS", t("tools_title"), t("tools_subtitle"))

tab_param = str(st.query_params.get("tab", "")).lower()
tab_order = ["compare", "prepay", "safety", "rejected"]
if tab_param in ["prepay", "safety", "rejected"]:
    tab_order.remove(tab_param)
    tab_order.insert(0, tab_param)

tab_labels = {
    "compare": t("tools_tab_compare"),
    "prepay": t("tools_tab_prepay"),
    "safety": t("tools_tab_safety"),
    "rejected": t("tools_tab_rejection"),
}

created_tabs = st.tabs([tab_labels[k] for k in tab_order])
tab_map = dict(zip(tab_order, created_tabs))
tab_compare = tab_map["compare"]
tab_prepay = tab_map["prepay"]
tab_safety = tab_map["safety"]
tab_rejection = tab_map["rejected"]

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
        {"name": "Offer A", "amt": def_amount, "rate": def_rate, "tenure": def_tenure, "feetype": t("fee_toggle_pct"), "feepct": 2.0, "feeamt": 6000.0, "other": 0.0, "accent": "offer-card-a"},
        {"name": "Offer B", "amt": def_amount, "rate": max(1.0, def_rate + 0.5), "tenure": def_tenure, "feetype": t("fee_toggle_pct"), "feepct": 0.5, "feeamt": 1500.0, "other": 0.0, "accent": "offer-card-b"},
        {"name": "Offer C", "amt": def_amount, "rate": max(1.0, def_rate - 0.25), "tenure": def_tenure, "feetype": t("fee_toggle_amt"), "feepct": 1.0, "feeamt": 2500.0, "other": 500.0, "accent": "offer-card-c"},
    ]

    for idx, col in enumerate(cols):
        i = idx + 1
        d = defaults[idx]
        with col:
            st.markdown(f'<div class="{d["accent"]}">', unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(f'<div class="wizard-card-title" style="font-size:20px !important;margin-bottom:12px !important;">{t("offer_label", n=i)}</div>', unsafe_allow_html=True)
                name_in = st.text_input(
                    t("offer_name"),
                    value=d["name"],
                    placeholder=t("offer_lender_placeholder"),
                    key=f"offer_name_{i}",
                )
                
                # 2-column input grid
                ig1, ig2 = st.columns(2)
                with ig1:
                    amt_in = st.number_input(
                        f"{t('loan_amount')} (₹)",
                        min_value=10000,
                        max_value=10000000,
                        value=int(d["amt"]),
                        step=25000,
                        key=f"offer_amt_{i}",
                    )
                with ig2:
                    rate_in = st.number_input(
                        t("rate"),
                        min_value=1.0,
                        max_value=50.0,
                        value=float(d["rate"]),
                        step=0.25,
                        key=f"offer_rate_{i}",
                    )

                ig3, ig4 = st.columns(2)
                with ig3:
                    tenure_in = st.number_input(
                        f"{t('tenure')} ({t('months')})",
                        min_value=6,
                        max_value=84,
                        value=int(d["tenure"]),
                        step=6,
                        key=f"offer_tenure_{i}",
                    )
                with ig4:
                    other_in = st.number_input(
                        t("other_charges"),
                        min_value=0.0,
                        max_value=100000.0,
                        value=float(d["other"]),
                        step=500.0,
                        key=f"offer_other_{i}",
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
            st.markdown('</div>', unsafe_allow_html=True)

    # Find cheapest offer
    cheapest = min(offers_data, key=lambda x: x["calc"]["total_cost"])

    st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

    # Clean HTML comparison card
    with st.container(border=True):
        st.markdown(f'<div class="wizard-card-title" style="font-size:22px !important;margin-bottom:14px !important;">{t("summary")}</div>', unsafe_allow_html=True)

        cols_head_html = []
        for o in offers_data:
            is_chp = (o["id"] == cheapest["id"])
            chp_cls = "highlight-col" if is_chp else ""
            badge_html = f'<div style="background:#1F7A4D;color:#FFFFFF;font-size:10px;padding:2px 8px;border-radius:999px;font-weight:700;display:inline-block;margin-bottom:4px;">{t("cheapest_badge")}</div><br>' if is_chp else ""
            cols_head_html.append(f'<th class="{chp_cls}">{badge_html}{o["name"]}</th>')

        def _row_html(title, values, highlight_idx=None):
            tds = []
            for idx, val in enumerate(values):
                cls = "highlight-col" if idx == highlight_idx else ""
                tds.append(f'<td class="{cls}">{val}</td>')
            return f'<tr><td>{title}</td>{"".join(tds)}</tr>'

        chp_idx = [idx for idx, o in enumerate(offers_data) if o["id"] == cheapest["id"]][0]

        rows_data = [
            (t("compare_row_emi"), [format_inr(o["calc"]["emi"]) for o in offers_data]),
            (t("compare_row_interest"), [format_inr(o["calc"]["total_interest"]) for o in offers_data]),
            (t("compare_row_fees"), [format_inr(o["calc"]["fees"]) for o in offers_data]),
            (t("compare_row_total_cost"), [f"<b>{format_inr(o['calc']['total_cost'])}</b>" for o in offers_data]),
            (t("compare_row_received"), [format_inr(o["calc"]["money_in_hand"]) for o in offers_data]),
            (t("compare_row_effective_rate"), [f"<b>{o['calc']['effective_annual_rate']:.2f}%</b>" for o in offers_data]),
        ]

        body_rows_html = "".join([_row_html(t_label, v_list, chp_idx) for t_label, v_list in rows_data])

        table_full_html = (
            f'<div style="overflow-x:auto;">'
            f'<table class="compare-clean-table">'
            f'<thead><tr><th>{t("summary")}</th>{"".join(cols_head_html)}</tr></thead>'
            f'<tbody>{body_rows_html}</tbody>'
            f'</table>'
            f'</div>'
        )
        st.markdown(table_full_html, unsafe_allow_html=True)

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

        st.markdown(
            f'<div style="background:#E7F4DD;border:1px solid #C6F24E;border-radius:12px;padding:12px 16px;margin:14px 0;font-size:14px;color:#1F7A4D;font-weight:600;">'
            f'{summary_sentence}'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div style="background:#F5F6F1;border:1px solid #E2E5DC;border-radius:12px;padding:12px 16px;font-size:13px;color:#4A554F;line-height:1.5;">'
            f'📄 <b>Key Fact Statement (KFS):</b> {t("kfs_tip_box")}'
            f'</div>',
            unsafe_allow_html=True,
        )
    render_feedback("tools_compare")


# ==============================================================================
# TAB B — Prepay early
# ==============================================================================
with tab_prepay:
    profile = st.session_state.get("profile", {})
    def_loan = float(profile.get("loan_amount", 300000))
    def_rate = float(profile.get("rate", 11.0))
    def_tenure = int(profile.get("tenure_months", 36))

    with st.container(border=True):
        st.markdown(f'<div class="wizard-card-title" style="font-size:20px !important;margin-bottom:14px !important;">{t("tools_tab_prepay")}</div>', unsafe_allow_html=True)
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

    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

    # 4 stat cards in a row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f'<div class="stat-box-card">'
            f'<div class="eyebrow-label">{t("prepay_stat_interest_saved")}</div>'
            f'<div class="stat-box-num" style="color:#1F7A4D;">{format_inr(res_p["interest_saved"])}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="stat-box-card">'
            f'<div class="eyebrow-label">{t("prepay_stat_charge_paid")}</div>'
            f'<div class="stat-box-num" style="color:#0F1B15;">{format_inr(res_p["charge_paid"])}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="stat-box-card">'
            f'<div class="eyebrow-label">{t("prepay_stat_net_saving")}</div>'
            f'<div class="stat-box-num" style="color:#0F1B15;">{format_inr(res_p["net_saving"])}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with m4:
        lbl_4 = t("prepay_stat_months_saved") if norm_mode == "tenure" else t("prepay_stat_new_emi")
        val_4 = f"{res_p['months_saved']} {t('months')}" if norm_mode == "tenure" else format_inr(res_p["new_emi"])
        st.markdown(
            f'<div class="stat-box-card">'
            f'<div class="eyebrow-label">{lbl_4}</div>'
            f'<div class="stat-box-num" style="color:#0F1B15;">{val_4}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

    # Chart in its own card
    with st.container(border=True):
        st.markdown(f'<div class="wizard-card-title" style="font-size:18px !important;margin-bottom:8px !important;">{t("prepay_chart_title")}</div>', unsafe_allow_html=True)
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
            line=dict(color="#1F7A4D", width=3),
        ))
        fig_prepay.update_layout(
            xaxis_title=t("months"),
            yaxis_title="₹",
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=10, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            font=dict(family="Inter, sans-serif"),
        )
        st.plotly_chart(fig_prepay, use_container_width=True, config={"displayModeBar": False})
        st.caption(t("prepay_rbi_rule_note"))

    render_feedback("tools_prepay")


# ==============================================================================
# TAB C — Is this loan app safe?
# ==============================================================================
with tab_safety:
    user_answers = []

    for idx, q_info in enumerate(SAFETY_QUESTIONS):
        i = idx + 1
        with st.container(border=True):
            col_q_text, col_q_ctrl = st.columns([1.5, 1], vertical_alignment="center")
            with col_q_text:
                st.markdown(f'<div style="font-size:15px;font-weight:600;color:var(--ink);">{t(q_info["key"])}</div>', unsafe_allow_html=True)
            with col_q_ctrl:
                ans = st.radio(
                    t(q_info["key"]),
                    [t("ans_yes"), t("ans_no"), t("ans_not_sure")],
                    index=2,
                    horizontal=True,
                    key=f"safety_q_{i}",
                    label_visibility="collapsed",
                )
                user_answers.append(ans)

    st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

    res_safety = app_safety_result(user_answers)
    status = res_safety["status"]

    if status == "red":
        st.markdown(f'<div style="background:#FBE7E2;border:1px solid #B5523B;border-radius:14px;padding:16px 20px;font-size:16px;color:#B5523B;font-weight:700;">🚨 {t("safety_res_red", n=res_safety["red_flags"])}</div>', unsafe_allow_html=True)
    elif status == "amber":
        st.markdown(f'<div style="background:#FDF1DC;border:1px solid #B7791F;border-radius:14px;padding:16px 20px;font-size:16px;color:#B7791F;font-weight:700;">⚠️ {t("safety_res_amber")}</div>', unsafe_allow_html=True)
    elif status == "incomplete":
        st.markdown(f'<div style="background:#FDF1DC;border:1px solid #B7791F;border-radius:14px;padding:16px 20px;font-size:16px;color:#B7791F;font-weight:700;">⚠️ {t("safety_res_incomplete")}</div>', unsafe_allow_html=True)
    elif status == "unanswered":
        st.markdown(f'<div style="background:#F5F6F1;border:1px solid #E2E5DC;border-radius:14px;padding:16px 20px;font-size:15px;color:#4A554F;font-weight:600;">ℹ️ {t("safety_res_unanswered")}</div>', unsafe_allow_html=True)
    elif status == "green":
        st.markdown(f'<div style="background:#E7F4DD;border:1px solid #1F7A4D;border-radius:14px;padding:16px 20px;font-size:16px;color:#1F7A4D;font-weight:700;">✅ {t("safety_res_green")}</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)

    # 4 link tiles in a 2x2 grid
    with st.container(border=True):
        st.markdown(f'<div class="wizard-card-title" style="font-size:18px !important;margin-bottom:12px !important;">{t("safety_how_to_check")}</div>', unsafe_allow_html=True)
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.markdown(f'<div style="background:#F8F9F6;border:1px solid #E2E5DC;border-radius:12px;padding:14px;margin-bottom:10px;"><a href="https://www.rbi.org.in" target="_blank" rel="noopener noreferrer" style="font-weight:700;color:var(--ink);text-decoration:none;">🏛️ {t("safety_link_rbi_directory")} ↗</a><div style="font-size:12px;color:var(--muted);margin-top:4px;">Official list of RBI-registered NBFCs and banks</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="background:#F8F9F6;border:1px solid #E2E5DC;border-radius:12px;padding:14px;margin-bottom:10px;"><a href="https://cms.rbi.org.in" target="_blank" rel="noopener noreferrer" style="font-weight:700;color:var(--ink);text-decoration:none;">⚖️ {t("safety_link_cms")} ↗</a><div style="font-size:12px;color:var(--muted);margin-top:4px;">File a complaint with RBI Ombudsman</div></div>', unsafe_allow_html=True)
        with col_v2:
            st.markdown(f'<div style="background:#F8F9F6;border:1px solid #E2E5DC;border-radius:12px;padding:14px;margin-bottom:10px;"><a href="https://sachet.rbi.org.in" target="_blank" rel="noopener noreferrer" style="font-weight:700;color:var(--ink);text-decoration:none;">⚠️ {t("safety_link_sachet")} ↗</a><div style="font-size:12px;color:var(--muted);margin-top:4px;">Report unauthorized digital lenders</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="background:#F8F9F6;border:1px solid #E2E5DC;border-radius:12px;padding:14px;margin-bottom:10px;"><a href="https://cybercrime.gov.in" target="_blank" rel="noopener noreferrer" style="font-weight:700;color:var(--ink);text-decoration:none;">🚨 {t("safety_link_cybercrime")} ↗</a><div style="font-size:12px;color:var(--muted);margin-top:4px;">Report harassment or extortion directly</div></div>', unsafe_allow_html=True)

    st.caption(t("safety_facts_line"))
    render_feedback("tools_safety")


# ==============================================================================
# TAB D — I got rejected
# ==============================================================================
with tab_rejection:
    st.markdown(f'<div class="wizard-card-title" style="font-size:22px !important;margin-bottom:12px !important;">{t("rej_title")}</div>', unsafe_allow_html=True)

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

    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f'<div class="wizard-card-title" style="font-size:20px !important;margin-bottom:6px !important;">{selected_label}</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:14px;color:var(--muted);line-height:1.5;margin-bottom:16px;"><b>{t("rej_card_meaning")}:</b> {t(f"rej_{selected_code}_meaning")}</p>', unsafe_allow_html=True)

        st.markdown(f'<div style="font-size:14px;font-weight:700;color:var(--ink);margin-bottom:10px;">{t("rej_card_steps")}</div>', unsafe_allow_html=True)
        for s_idx in [1, 2, 3]:
            st.markdown(
                f'<div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:10px;font-size:14px;line-height:1.5;color:var(--ink);">'
                f'<span class="num-circle-lime">{s_idx}</span>'
                f'<div>{t(f"rej_{selected_code}_step{s_idx}")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<div style="display:inline-block;background:#F5F6F1;border:1px solid #E2E5DC;border-radius:999px;padding:6px 14px;font-size:13px;color:var(--muted);margin-top:10px;">'
            f'⏱️ <b>{t("rej_card_wait")}:</b> {t(f"rej_{selected_code}_wait")}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
    if st.button(t("rej_btn_check"), type="primary", use_container_width=True, key="btn_rej_to_check"):
        try:
            st.switch_page("pages/1_Check_Eligibility.py")
        except Exception:
            pass

    render_feedback("tools_rejection")

st.markdown('</div>', unsafe_allow_html=True)
footer()
