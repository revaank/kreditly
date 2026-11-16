"""Turn model factors into short, translated reasons and tips."""
from .finance import format_inr
from .translations import t

def explain_reasons(features: dict):
    """Return up to five meaningful facts, ordered by how unusual they are."""
    loan=features["loan_to_income"]; dti=features["dti"]
    util=features["revol_util"]; history=features["credit_history_years"]
    job=features["emp_length"]
    candidates=[
      ("loan_to_income",loan>1.5,t("reason_loan",x=f"{loan:.1f}") if loan>1.5 else t("reason_low_loan"),abs(loan-1.0)),
      ("dti",dti>20,t("reason_dti",x=f"{dti:.0f}") if dti>20 else t("reason_low_dti"),abs(dti-10)/10),
      ("revol_util",util>50,t("reason_util",x=f"{util:.0f}") if util>50 else t("reason_low_util"),abs(util-30)/30),
      ("pub_rec",features["pub_rec"]>0,t("reason_records") if features["pub_rec"] else t("reason_no_records"),features["pub_rec"]),
      ("pub_rec_bankruptcies",features["pub_rec_bankruptcies"]>0,t("reason_bankruptcy"),features["pub_rec_bankruptcies"]),
      ("credit_history_years",history<3,t("reason_short_history") if history<3 else t("reason_history") if history>=8 else t("reason_mid_history"),1 if history<3 else min(1,history/8)),
      ("emp_length",job<2,t("reason_short_job") if job<2 else t("reason_job"),1 if job<2 else min(1,job/5)),
      ("mort_acc",False,t("reason_mortgage"),features["mort_acc"]),
      ("term",features["term"]==60,t("reason_term") if features["term"]==60 else t("reason_short_term"),.7 if features["term"]==60 else .2)]
    candidates.sort(key=lambda item:item[3],reverse=True)
    return [{"feature":key,"helpful":not harmful,"text":sentence} for key,harmful,sentence,_ in candidates[:5]]

def improvement_tips(values: dict):
    tips=[]
    if values.get("existing_emi",0)>0: tips.append(t("tip_emi",x=format_inr(values["existing_emi"]*.15)))
    if values.get("loan_amount",0)>0: tips.append(t("tip_loan",x=format_inr(values["loan_amount"]*.75)))
    if values.get("card_bill",0)>0: tips.append(t("tip_card",x=format_inr(values["card_bill"]*.3)))
    return tips[:3]
