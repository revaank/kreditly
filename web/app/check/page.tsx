"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { type KeyboardEvent, useEffect, useState } from "react";
import { Footer } from "../../components/footer";
import { Header } from "../../components/header";
import { Button } from "../../components/ui/button";
import { loadProfile, money, type Profile, storeProfile } from "../../lib/profile";
import { useLanguage } from "../providers";

type Field = keyof Profile;
const questions: { field: Field; section: number; kind: "number" | "money" | "select"; min?: number; max?: number; options?: [string, string | number | boolean][]; why: string }[] = [
  {field:"age",section:0,kind:"number",min:21,max:65,why:"ageWhy"},
  {field:"employment",section:0,kind:"select",options:[["salary","Salaried"],["self","Self-employed"]],why:"employmentWhy"},
  {field:"job_years",section:0,kind:"number",min:0,max:60,why:"jobWhy"},
  {field:"home",section:0,kind:"select",options:[["rented","rented"],["own","own"],["own_loan","own_loan"]],why:"homeWhy"},
  {field:"credit_year",section:0,kind:"number",min:1950,max:2026,why:"creditYearWhy"},
  {field:"credit_unknown",section:0,kind:"select",options:[["no",false],["yes",true]],why:"creditUnknownWhy"},
  {field:"annual_income",section:1,kind:"money",min:1,why:"incomeWhy"},
  {field:"existing_emi",section:1,kind:"money",min:0,why:"emiWhy"},
  {field:"card_bill",section:1,kind:"money",min:0,why:"cardBillWhy"},
  {field:"revol_util",section:1,kind:"number",min:0,max:100,why:"utilWhy"},
  {field:"open_acc",section:1,kind:"number",min:0,max:100,why:"openWhy"},
  {field:"total_acc",section:1,kind:"number",min:0,max:150,why:"totalWhy"},
  {field:"mort_acc",section:1,kind:"number",min:0,max:50,why:"mortWhy"},
  {field:"pub_rec",section:1,kind:"number",min:0,max:50,why:"pubWhy"},
  {field:"bankruptcies",section:1,kind:"number",min:0,max:20,why:"bankruptcyWhy"},
  {field:"cibil_index",section:1,kind:"select",options:[["excellent",0],["good",1],["average",2],["low",3],["unknown",4]],why:"cibilWhy"},
  {field:"loan_amount",section:2,kind:"money",min:1,why:"loanWhy"},
  {field:"tenure_months",section:2,kind:"select",options:[["months",12],["months",24],["months",36],["months",48],["months",60]],why:"tenureWhy"},
  {field:"purpose",section:2,kind:"select",options:[["debt","debt_consolidation"],["card","credit_card"],["homeImprove","home_improvement"],["purchase","major_purchase"],["business","small_business"],["vehicle","car"],["medical","medical"],["other","other"]],why:"purposeWhy"},
  {field:"rate",section:2,kind:"number",min:0,max:40,why:"rateWhy"},
];
const sectionNames = ["about","finances","loan"];
const currencyFields: Field[] = ["annual_income","existing_emi","card_bill","loan_amount"];

export default function CheckPage() {
  const t = useTranslations(); const app = useTranslations("app"); const router = useRouter(); const { language } = useLanguage();
  const [profile,setProfile] = useState<Profile>(loadProfile); const [step,setStep] = useState(0); const [rawValues,setRawValues] = useState<Record<string,string>>({}); const [error,setError] = useState(false);
  const question = questions[step];
  useEffect(() => { const query = Number(new URLSearchParams(window.location.search).get("step")); if (query >= 0 && query < questions.length) setStep(query); }, []);
  const section = question.section;
  const raw = rawValues[question.field] ?? (currencyFields.includes(question.field) ? money(Number(profile[question.field])) : String(profile[question.field] ?? ""));
  const setValue = (value: string | number | boolean) => {
    const parsed = question.kind === "number" || question.kind === "money" ? Number(String(value).replaceAll(",", "")) : value;
    setProfile(old => ({...old,[question.field]: parsed, ...(question.field === "cibil_index" ? {cibil: ["Excellent · 750+","Good · 700–749","Average · 650–699","Low · below 650","Don't know"][Number(parsed)], cibil_unknown: Number(parsed)===4} : {})} as Profile));
    setRawValues(old=>({...old,[question.field]:currencyFields.includes(question.field) && String(value).replaceAll(",", "") ? money(Number(String(value).replaceAll(",", ""))) : String(value)})); setError(false);
  };
  const advance = (direction: number) => {
    const numeric = question.kind === "money" || question.kind === "number";
    const numericValue = Number(String(raw).replaceAll(",", ""));
    if (numeric && (Number.isNaN(numericValue) || (question.min !== undefined && numericValue < question.min) || (question.max !== undefined && numericValue > question.max))) { setError(true); return; }
    if (question.field === "open_acc" && numericValue > profile.total_acc) { setError(true); return; }
    const next = step + direction;
    if (next < 0) { router.push("/"); return; }
    if (next >= questions.length) { const updated = {...profile,language}; storeProfile(updated); router.push("/results"); return; }
    setStep(next); router.replace(`/check?step=${next}`); window.scrollTo({top:0,behavior:"smooth"});
  };
  const onKey = (event: KeyboardEvent<HTMLInputElement>) => { if(event.key === "Enter") { event.preventDefault(); advance(1); } };
  const label = (key: string, values?: Record<string, string | number>) => t(`form.${key}`, values as never);
  const selectLabel = (rawValue: string | number) => {
    if(question.field === "employment") return label(String(rawValue)==="Salaried"?"salary":"self");
    if(question.field === "home") return label(String(rawValue));
    if(question.field === "credit_unknown") return label(String(rawValue)==="true"?"yes":"no");
    if(question.field === "cibil_index") return label(["excellent","good","average","low","unknown"][Number(rawValue)]);
    if(question.field === "purpose") return label(({debt_consolidation:"debt",credit_card:"card",home_improvement:"homeImprove",major_purchase:"purchase",small_business:"business",car:"vehicle",medical:"medical",other:"other"} as Record<string,string>)[String(rawValue)]);
    if(question.field === "tenure_months") return label("months",{count:Number(rawValue)});
    return String(rawValue);
  };
  const progress = (step+1)/questions.length*100;
  return <div className="page-shell"><Header/><main className="container"><div className="page-top"><span className="small-label">{t("form.progress",{current:step+1,total:questions.length})}</span><h1>{label(sectionNames[section])}</h1><p className="muted">A private, educational estimate. You can go back and change any answer.</p></div>
    <p className="muted">{app("formPrivacy")}</p><div className="form-layout"><aside className="checklist" aria-label={label("progress",{current:step+1,total:questions.length})}>{sectionNames.map((name,index)=><div className={index===section?"checklist-item active":"checklist-item"} key={name}>{label(name)}</div>)}</aside>
      <section className="question-card"><div className="progress-track" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round(progress)}><span style={{width:`${progress}%`}}/></div><span className="small-label">{t("form.progress",{current:step+1,total:questions.length})}</span><h2>{label(question.field==="credit_unknown"?"creditUnknownTitle":String(question.field))}</h2>
        {question.kind === "select" ? <div className="select-options">{question.options?.map(([optionKey,value])=><button type="button" key={`${value}`} className={String(profile[question.field])===String(value)?"option-button selected":"option-button"} onClick={()=>setValue(value)}>{question.field==="tenure_months"?label("months",{count:Number(value)}):label(String(optionKey))}</button>)}</div> : <div className={question.kind==="money"?"money-wrap":""}>{question.kind==="money"&&<span className="money-symbol">₹</span>}<input className="question-input" type="text" inputMode="decimal" value={raw} min={question.min} max={question.max} onChange={e=>setValue(e.target.value)} onKeyDown={onKey} aria-label={label(String(question.field))}/>{question.field==="annual_income"&&<p className="muted">{t("form.incomeMonthly",{amount:money(Number(String(raw).replaceAll(",",""))/12)})}</p>}{question.field==="annual_income"&&<div className="quick-picks"><button type="button" className="quick-pick" onClick={()=>setValue(800000)}>{label("quickIncome")}</button></div>}{question.field==="loan_amount"&&<div className="quick-picks"><button type="button" className="quick-pick" onClick={()=>setValue(300000)}>{label("quickLoan")}</button></div>}</div>}
        {error&&<p role="alert" className="error-text">{label("errors")}</p>}
        <div className="form-actions"><Button type="button" variant="outline" className="button button-white" onClick={()=>advance(-1)}>{label("back")}</Button><Button type="button" variant="lime" className="button button-lime" onClick={()=>advance(1)}>{step===questions.length-1?label("finish"):label("continue")}</Button></div>
      </section><aside className="why-card"><h3>{label("why")}</h3><p>{label(question.why)}</p></aside>
    </div></main><Footer/></div>;
}
