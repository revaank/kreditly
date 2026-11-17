"""Three-step profile form, educational estimate and what-if controls."""
from urllib.parse import quote
import streamlit as st
from src.counterfactual import apply_change, find_improvements
from src.bank_checker import count_meets, load_bank_rules
from src.bank_ui import render_bank_results
from src.explainer import explain_reasons, suggestion_text
from src.features import build_features
from src.finance import format_inr, loan_summary, foir
from src.predictor import explain, predict
from src.translations import t
from src.ui import contribution_chart, footer, header, money_input, page_setup, render_emi_planner, render_whatif_result, result_card, section_title

page_setup(); header("check")
section_title(t("check_title"))

def reset_whatif():
    for key in ("whatif_income","whatif_loan","whatif_emi","whatif_util","whatif_tenure"):
        st.session_state.pop(key,None)

def save_credit_unknown(widget_key):
    """Keep the unknown-year choice in the profile when its localized widget hides."""
    st.session_state.profile["credit_unknown"]=bool(st.session_state.get(widget_key,False))

if "form_step" not in st.session_state: st.session_state.form_step=1
if "profile" not in st.session_state:
    st.session_state.profile={"age":30,"employment":"Salaried","job_years":5,"home":"Rented","credit_year":2015,"annual_income":800000,"existing_emi":5000,"card_bill":12000,"revol_util":30,"open_acc":3,"total_acc":8,"mort_acc":0,"pub_rec":0,"bankruptcies":0,"cibil":"Good · 700–749","loan_amount":300000,"tenure_months":36,"purpose":"Other","rate":11.0}
v=st.session_state.profile
steps=[t("step_about"),t("step_finances"),t("step_loan")]
st.progress(st.session_state.form_step/3,text=f"{st.session_state.form_step} / 3 · {steps[st.session_state.form_step-1]}")
st.markdown(" · ".join([f"**{s}**" if i+1==st.session_state.form_step else s for i,s in enumerate(steps)]))

left,right=st.columns([1.55,1],gap="large")
with left:
    with st.container(border=True):
        if st.session_state.form_step==1:
            a,b=st.columns(2)
            with a: v["age"]=st.number_input(t("age"),18,100,int(v["age"]))
            employment_options=[t("salaried"),t("self_employed")]
            employment_index=int(v.get("employment_index",0 if v.get("employment") in ("Salaried","वेतनभोगी") else 1))
            with b: selected_employment=st.selectbox(t("employment"),employment_options,index=employment_index)
            v["employment_index"]=employment_options.index(selected_employment)
            v["employment"]="Salaried" if v["employment_index"]==0 else "Self-employed"
            years=["<1", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10+"]
            with a: job=st.selectbox(t("job_years"),years,index=min(int(v["job_years"]),10))
            with b: home_label=st.selectbox(t("home"),[t("rented"),t("own"),t("own_loan")],index={"rented":0,"own":1,"own_loan":2}.get(v["home"],0))
            v["job_years"]=0 if job=="<1" else (10 if job=="10+" else int(job)); v["home"]={t("rented"):"rented",t("own"):"own",t("own_loan"):"own_loan"}[home_label]
            v["credit_year"]=st.number_input(t("credit_year"),1980,2026,int(v["credit_year"]))
            # Streamlit clears the state of widgets hidden on earlier wizard steps.
            # Re-hydrate this checkbox from the profile dictionary when returning.
            credit_unknown_key=f"credit_unknown_{st.session_state.language}"
            if credit_unknown_key not in st.session_state:
                st.session_state[credit_unknown_key]=bool(v.get("credit_unknown",False))
            v["credit_unknown"]=st.checkbox(t("dont_know"),key=credit_unknown_key,on_change=save_credit_unknown,args=(credit_unknown_key,))
        elif st.session_state.form_step==2:
            a,b=st.columns(2)
            with a: v["annual_income"],v["_income_valid"]=money_input(t("income"),"income",v["annual_income"])
            with b: v["existing_emi"],v["_emi_valid"]=money_input(t("existing_emi"),"existing_emi",v["existing_emi"])
            with a: v["card_bill"],v["_card_valid"]=money_input(t("card_bill"),"card_bill",v["card_bill"])
            usage=[t("very_little"),t("third"),t("half"),t("almost_all"),t("no_card")]; usage_vals=[10,30,50,90,0]
            with b: use=st.selectbox(t("card_usage"),usage,index=usage_vals.index(v["revol_util"]) if v["revol_util"] in usage_vals else 0)
            v["revol_util"]=usage_vals[usage.index(use)]
            a,b=st.columns(2)
            with a: v["open_acc"]=st.number_input(t("open_accounts"),min_value=0,max_value=100,value=int(v["open_acc"]))
            with b: v["total_acc"]=st.number_input(t("total_accounts"),min_value=0,max_value=150,value=int(v["total_acc"]))
            with a: v["mort_acc"]=st.number_input(t("mort_accounts"),min_value=0,max_value=50,value=int(v["mort_acc"]))
            with b: v["pub_rec"]=st.number_input(t("public_records"),min_value=0,max_value=50,value=int(v["pub_rec"]))
            with a: v["bankruptcies"]=st.number_input(t("bankruptcies"),min_value=0,max_value=20,value=int(v["bankruptcies"]))
            cibil=[t("excellent"),t("good"),t("average"),t("low"),t("dont_know")]
            cibil_index=int(v.get("cibil_index",1))
            with b: c=st.selectbox(t("cibil"),cibil,index=cibil_index)
            v["cibil"]=c; v["cibil_index"]=cibil.index(c); st.caption(t("cibil_help"))
            v["cibil_unknown"]=v["cibil_index"]==4
        else:
            a,b=st.columns(2)
            with a: v["loan_amount"],v["_loan_valid"]=money_input(t("loan_amount"),"loan",v["loan_amount"])
            with b: tenure=st.selectbox(t("tenure"),[36,60],index=0 if v["tenure_months"]==36 else 1,format_func=lambda n:f"{n} {t('months')}")
            v["tenure_months"]=tenure
            purposes=[t("p_debt"),t("p_card"),t("p_home"),t("p_purchase"),t("p_business"),t("p_vehicle"),t("p_medical"),t("p_other")]
            purpose_codes=["debt_consolidation","credit_card","home_improvement","major_purchase","small_business","car","medical","other"]
            p=st.selectbox(t("purpose"),purposes,index=purpose_codes.index(v["purpose"]) if v["purpose"] in purpose_codes else 7)
            v["purpose"]=purpose_codes[purposes.index(p)]
            v["rate"]=st.number_input(t("rate"),min_value=0.0,max_value=40.0,step=.5,value=float(v["rate"]))
        if st.session_state.get("validation_error"):
            st.error(t(st.session_state.validation_error)); st.session_state.validation_error=None
        x,y=st.columns(2)
        with x:
            if st.session_state.form_step>1 and st.button(t("back"),use_container_width=True): st.session_state.form_step-=1; st.rerun()
        with y:
            if st.session_state.form_step<3:
                if st.button(t("continue"),type="primary",use_container_width=True):
                    if st.session_state.form_step==2 and not all(v.get(key,True) for key in ("_income_valid","_emi_valid","_card_valid")): st.session_state.validation_error="money_input_hint"
                    elif st.session_state.form_step==2 and v["annual_income"]<=0: st.session_state.validation_error="income_positive"
                    elif st.session_state.form_step==2 and v["open_acc"]>v["total_acc"]: st.session_state.validation_error="accounts_check"
                    else: st.session_state.form_step+=1
                    st.rerun()
            elif st.button(t("run_check"),type="primary",use_container_width=True):
                if not v.get("_loan_valid",True): st.session_state.validation_error="money_input_hint"; st.rerun()
                if v["loan_amount"]<=0: st.session_state.validation_error="loan_positive"; st.rerun()
                with st.spinner(t("checking")):
                    try:
                        features=build_features(v)
                        prediction=predict(features)
                    except Exception:
                        st.session_state.validation_error="model_error"
                        st.rerun()
                    st.session_state.estimate={"features":features,"result":prediction,"values":dict(v)}
                st.rerun()

summary=loan_summary(v["loan_amount"],v["rate"],v["tenure_months"])
monthly_income=v["annual_income"]/12
ratio=foir(monthly_income,v["existing_emi"],summary["emi"])
with right:
    if st.session_state.form_step >= 3:
        st.markdown(f'<div class="panel"><div class="small-label">{t("summary")}</div><h3>{format_inr(summary["emi"])} <span class="muted" style="font-size:14px">{t("per_month")}</span></h3><p>{t("monthly_emi")}</p><hr><p>{t("total_interest")}: <b>{format_inr(summary["interest"])}</b></p><p>{t("total_repayment")}: <b>{format_inr(summary["total"])}</b></p><p>{t("salary_emi")}: <b>{ratio:.1f}%</b></p></div>',unsafe_allow_html=True)
        meter_tone="safe" if ratio<35 else "watch" if ratio<=50 else "high"
        st.markdown(f'<div class="afford-track"><div class="afford-fill {meter_tone}" style="width:{min(100,max(0,ratio))}%"></div></div>',unsafe_allow_html=True)
        st.caption(t("afford_ok") if ratio<35 else t("afford_mid") if ratio<=50 else t("afford_high"))

if "estimate" in st.session_state:
    st.markdown("---"); estimate=st.session_state.estimate; result=estimate["result"]; values=estimate["values"]; features=estimate["features"]
    st.info(t("model_warning"))
    if values.get("credit_unknown") or values.get("cibil_unknown"): st.info(t("estimated"))
    col1,col2=st.columns([1,1.15],gap="large")
    with col1: result_card(result)
    with col2:
        section_title(t("why"))
        try:
            contributions=explain(features)
            for reason in explain_reasons(features,contributions): st.markdown(("✅ " if reason["helpful"] else "⚠️ ")+reason["text"])
        except Exception:
            contributions=[]
            st.warning(t("explanation_error"))
    section_title(t("contributions"))
    contribution_chart(contributions)
    if result["label"]!="STRONG":
        section_title(t("improve"))
        try:
            suggestions=find_improvements(values)
            if suggestions:
                for suggestion in suggestions:
                    st.markdown("• "+" + ".join(suggestion_text(change) for change in suggestion["changes"]))
            else:
                st.caption(t("no_counterfactual"))
        except Exception:
            st.caption(t("model_error"))
        st.caption(t("recommendation_note"))
    section_title(t("whatif"))
    signature=tuple(values.get(key) for key in ("annual_income","loan_amount","tenure_months","existing_emi","revol_util"))
    if st.session_state.get("whatif_signature")!=signature:
        reset_whatif(); st.session_state.whatif_signature=signature
    with st.container(border=True):
        col1,col2=st.columns(2)
        with col1:
            income=st.slider(t("income")+" (₹)",min_value=max(1,int(values["annual_income"]*.5)),max_value=max(2000000,int(values["annual_income"]*1.5)),value=int(values["annual_income"]),step=25000,key="whatif_income",format="₹%d")
            st.caption(format_inr(income))
        with col2:
            loan=st.slider(t("loan_amount")+" (₹)",min_value=max(1,min(50000,int(values["loan_amount"]*.5))),max_value=max(5000000,int(values["loan_amount"]*1.5)),value=int(values["loan_amount"]),step=25000,key="whatif_loan",format="₹%d")
            st.caption(format_inr(loan))
        col1,col2=st.columns(2)
        with col1:
            emi_old=st.slider(t("existing_emi")+" (₹)",0,max(100000,int(values["existing_emi"]*2+1000)),int(values["existing_emi"]),step=1000,key="whatif_emi",format="₹%d")
            st.caption(format_inr(emi_old))
        with col2:
            util=st.slider(t("card_usage"),0,100,int(values["revol_util"]),step=5,key="whatif_util")
            st.caption(f"{util}%")
        tenure=st.select_slider(t("slider_tenure"),options=[36,60],value=int(values["tenure_months"]),format_func=lambda n:f"{n} {t('months')}",key="whatif_tenure")
        try:
            new_values,new_result=apply_change(values,income=income,loan=loan,months=tenure,existing_emi=emi_old,revol_util=util)
        except Exception:
            new_values=dict(values)
            new_values.update({"annual_income":income,"loan_amount":loan,"tenure_months":tenure,"existing_emi":emi_old,"revol_util":util})
            new_result=None
            st.warning(t("model_error"))
        new_emi=loan_summary(loan,values["rate"],tenure)["emi"]; new_foir=foir(income/12,emi_old,new_emi)
        if new_result:
            render_whatif_result(new_result,result)
            status_label=t(f"readiness_{new_result.get('readiness_band','fair')}")
            st.caption(f'{t("monthly_emi")}: {format_inr(new_emi)} · {t("salary_emi")}: {new_foir:.1f}% · {status_label}')
        st.button(t("reset"),on_click=reset_whatif)
        render_bank_results(new_values,compact=True)
    render_emi_planner(values["loan_amount"], values["rate"], values["tenure_months"])
    bank_results=render_bank_results(values)
    label_key={"STRONG":"strong","BORDERLINE":"borderline","RISKY":"risky"}[result["label"]]
    report_lines=[
        t("report"),t("report_dummy"),
        t("readiness_result",band=t(f"readiness_{result.get('readiness_band','fair')}")),
        f'{t("risk_details")}: {t("calibrated_risk")} {result["risk"]:.0%} ({t(label_key)})',
        f'{t("monthly_emi")}: {format_inr(summary["emi"])}',
        f'{t("salary_emi")}: {ratio:.1f}%',
    ]
    if bank_results is not None:
        report_lines.append(t("bank_summary",count=count_meets(bank_results),total=len(bank_results)))
        report_lines.extend(f'{item["name"]}: {t("bank_status_"+item["status"])}' for item in bank_results)
        bank_metadata=load_bank_rules()
        report_lines.extend([t("bank_last_checked",date=bank_metadata.get("last_checked","")),t("bank_disclaimer")])
    report_lines.append(t("report_no_personal"))
    report="\n".join(report_lines)
    actions=st.columns(2)
    with actions[0]: st.download_button(t("download"),report,file_name="kreditly-estimate.txt",mime="text/plain",use_container_width=True)
    with actions[1]: st.link_button(t("whatsapp"),"https://wa.me/?text="+quote(t("wa_summary",band=t(f"readiness_{result.get('readiness_band','fair')}"))),use_container_width=True)
footer()
