"use client";

import { Check, CircleX, Printer, Share2, SlidersHorizontal, TriangleAlert, X } from "lucide-react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Footer } from "../../components/footer";
import { Header } from "../../components/header";
import { Dialog, DialogClose, DialogContent, DialogDescription, DialogOverlay, DialogPortal, DialogTitle } from "../../components/ui/dialog";
import { apiRequest, type Lender, type LendersResponse, type Prediction, profilePayload } from "../../lib/api";
import { apiBase, loadProfile, money, type Profile } from "../../lib/profile";
import { useLanguage } from "../providers";

type WhatIfResult = Prediction & { delta: { risk: number; from_band: string } };
type EmiRow = { months: number; emi: number; interest: number; total: number };

function requirementText(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") return value.toLocaleString("en-IN",{maximumFractionDigits:2});
  if (typeof value === "string") return value;
  if (typeof value === "object") {
    const object = value as Record<string,unknown>;
    if (Array.isArray(object.value)) return object.value.join(", ");
    const base = object.value !== undefined ? requirementText(object.value) : "";
    const existing = object.existing_customer_value !== undefined ? ` · salary-account customers: ${requirementText(object.existing_customer_value)}` : "";
    return `${base}${existing}${object.at_maturity ? " at loan maturity" : ""}`;
  }
  return String(value);
}

export default function ResultsPage() {
  const t = useTranslations("results"); const app = useTranslations("app"); const {language} = useLanguage();
  const [profile,setProfile] = useState<Profile>(loadProfile);
  const [prediction,setPrediction] = useState<Prediction|null>(null);
  const [lenders,setLenders] = useState<LendersResponse|null>(null);
  const [emiRows,setEmiRows] = useState<EmiRow[]>([]);
  const [loading,setLoading] = useState(true); const [slow,setSlow] = useState(false); const [error,setError] = useState(false);
  const [selected,setSelected] = useState<Lender|null>(null); const [planner,setPlanner] = useState(false);
  const [whatValues,setWhatValues] = useState({loan_amount:0,existing_emi:0,revol_util:0,tenure_months:0});
  const [whatResult,setWhatResult] = useState<WhatIfResult|null>(null); const [whatBanks,setWhatBanks] = useState<number|null>(null); const [whatLoading,setWhatLoading] = useState(false);

  useEffect(()=>{const current=loadProfile();current.language=language;setProfile(current);setWhatValues({loan_amount:current.loan_amount,existing_emi:current.existing_emi,revol_util:current.revol_util,tenure_months:current.tenure_months});},[language]);
  useEffect(()=>{
    let active=true; const timer=window.setTimeout(()=>{if(active)setSlow(true);},3000);
    setLoading(true);setError(false);
    const current=loadProfile(); current.language=language;
    Promise.all([
      apiRequest<Prediction>("/predict",profilePayload(current,language)),
      apiRequest<LendersResponse>("/lenders",profilePayload(current,language)),
      apiRequest<{terms:EmiRow[]}>(`/emi-table?amount=${current.loan_amount}&rate=${current.rate}`),
    ]).then(([estimate,bankData,emiData])=>{if(!active)return;setPrediction(estimate);setLenders(bankData);setEmiRows(emiData.terms);})
      .catch(()=>{if(active)setError(true);}).finally(()=>{if(active){setLoading(false);window.clearTimeout(timer);}});
    return ()=>{active=false;window.clearTimeout(timer);};
  },[language]);

  useEffect(()=>{
    if(!planner)return;
    const timer=window.setTimeout(async()=>{
      setWhatLoading(true);
      try {
        const changed={...profile,...whatValues}; const payload=profilePayload(changed,language);
        const [result,bankData]=await Promise.all([
          apiRequest<WhatIfResult>("/whatif",{profile:profilePayload(profile,language),changes:whatValues}),
          apiRequest<LendersResponse>("/lenders",payload),
        ]);
        setWhatResult(result);setWhatBanks(bankData.qualify_count);
      } catch { setWhatResult(null);setWhatBanks(null); } finally {setWhatLoading(false);}
    },300);
    return ()=>window.clearTimeout(timer);
  },[planner,whatValues,profile,language]);

  const sortedLenders=useMemo(()=>[...(lenders?.lenders??[])].sort((a,b)=>({qualify:0,close:1,miss:2}[a.status]-{qualify:0,close:1,miss:2}[b.status])),[lenders]);
  const statusText=(status:Lender["status"])=>status==="qualify"?t("meets"):status==="close"?t("closeStatus"):t("miss");
  const printReport=()=>window.print();
  const share=()=>window.open(`https://wa.me/?text=${encodeURIComponent(`Kreditly estimate: ${prediction?.readiness_band ?? ""}. Educational estimate only: ${window.location.href}`)}`,"_blank","noopener,noreferrer");
  const updateWhat=(field:keyof typeof whatValues,value:number)=>setWhatValues(old=>({...old,[field]:value}));

  return <div className="page-shell"><Header/><main className="container">
    <div className="results-toolbar"><Link className="button button-white button-small" href="/check">{t("edit")}</Link><div className="toolbar-actions"><button type="button" className="button button-white button-small" onClick={printReport}><Printer size={16}/>{t("pdf")}</button><button type="button" className="button button-white button-small" onClick={share}><Share2 size={16}/>{t("share")}</button></div></div>
    <div className="results-title"><h1>{t("title")}</h1><p className="muted">{t("disclaimer")}</p></div>
    {loading&&<section className="loading-card" aria-live="polite"><p>{slow?t("waking"):t("loading")}</p><div className="skeleton large"/><div className="skeleton"/><div className="skeleton"/></section>}
    {error&&!loading&&<section className="error-card" role="alert"><h2>{t("error")}</h2><p className="muted">API: {apiBase}</p><button type="button" className="button button-lime" onClick={()=>window.location.reload()}>{t("errorRetry")}</button></section>}
    {!loading&&!error&&prediction&&lenders&&<>
      <section className="results-grid">
        <article className="dark-result"><div className="band-line"><h2>{t("readiness")}</h2><span className="band-chip">{t(`band_${prediction.readiness_band}`)}</span></div><div className="big-number">{t(`band_${prediction.readiness_band}`)}</div><div className="result-meter"><span style={{width:`${Math.max(5,Math.min(100,prediction.probability*100))}%`}}/></div><p className="result-note">{t("risk")}: {(prediction.probability*100).toFixed(1)}%. {app("modelCaveat")}</p></article>
        <article className="light-card"><h2>{t("emi")}</h2><div className="big-number" style={{color:"var(--ink)"}}>₹{money(prediction.finance.emi)}</div><p className="muted">{t("salaryBar")}</p><div className="foir-track"><span style={{width:`${Math.max(2,Math.min(100,prediction.finance.foir))}%`}}/></div><div className="band-line"><span className="muted">FOIR {prediction.finance.foir.toFixed(1)}%</span><span className="tag">{t("mostLenders")}</span></div><p style={{marginTop:16}}>{t("interest")}: <strong>₹{money(prediction.finance.total_interest)}</strong></p></article>
      </section>
      <section className="section" style={{paddingBottom:28}}><div className="section-heading-row"><h2>{t("fixes")}</h2><span className="muted">{app("suggestionCaveat")}</span></div><div className="fix-list">{prediction.suggestions.length?prediction.suggestions.map((item,index)=><article className={index===0?"fix-card featured":"fix-card"} key={item.field}>{index===0&&<span className="tag">{t("biggest")}</span>}<p>{item.text}</p></article>):<article className="fix-card"><p>{t("noFixes")}</p></article>}</div></section>
      <section className="section" style={{paddingTop:24}}><div className="section-heading-row"><div><h2>{t("lendersTitle")}</h2><p className="section-intro">{t("meetCount",{count:lenders.qualify_count,total:lenders.total})}</p></div><button type="button" className="button button-lime" onClick={()=>setPlanner(true)}><SlidersHorizontal size={17}/>{t("planner")}</button></div>
        <p className="muted">{language==="hi"?app("bankDisclaimer"):lenders.disclaimer} · {app("lastChecked",{date:lenders.last_checked??"—"})}</p><p className="muted">{t("criteriaNote")}</p>
        <div className="lender-grid">{sortedLenders.map(lender=>{
          const stateClass=lender.status==="qualify"?"success":lender.status==="close"?"warning":"danger";
          const explanation=lender.fixes[0]??t("reason");
          const rate=lender.interest_rate_from===null?t("checkRate"):t("from",{rate:Number(lender.interest_rate_from).toFixed(2)});
          return <article className="lender-card" key={lender.id}><div className="lender-top"><div><span className="small-label">{lender.type==="NBFC"?t("nbfc"):t("bank")}</span><h3>{lender.name}</h3></div><span className={`tag ${stateClass}`}>{statusText(lender.status)}</span></div><p>{lender.product}</p><p><strong>{rate}</strong></p><p className="lender-reason">{explanation}</p><button type="button" className="inline-link" onClick={()=>setSelected(lender)}>{t("criteria")}</button></article>;
        })}</div>
        <p className="footer-warning">{t("footer")}</p>
      </section>
      <section className="section"><h2>{t("factors")}</h2><div className="explain-grid">{prediction.top_factors.map((factor)=><article className={factor.helpful?"factor-card":"factor-card hurts"} key={factor.feature}><div className="factor-heading"><span>{app(`feature_${factor.feature}`)}</span><span>{factor.helpful?t("helps"):t("hurts")}</span></div><p className="muted" style={{fontSize:13,margin:"9px 0 0"}}>{factor.text}</p><div className="bar-track"><span style={{width:`${Math.max(8,Math.min(100,Math.abs(factor.contribution)*300))}%`}}/></div></article>)}</div></section>
      <section className="section"><h2>{t("emiChart")}</h2><div className="chart-card"><ResponsiveContainer width="100%" height={290}><BarChart data={emiRows} margin={{top:18,right:12,left:0,bottom:4}}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E5DC"/><XAxis dataKey="months" tickFormatter={(n)=>`${n}m`} tickLine={false} axisLine={false}/><YAxis tickFormatter={(n)=>`₹${Math.round(Number(n)/1000)}k`} width={55} tickLine={false} axisLine={false}/><Tooltip formatter={(value)=>`₹${money(Number(value))}`}/><Bar dataKey="emi" name={t("emi")} radius={[7,7,0,0]} fill="#92b838"/></BarChart></ResponsiveContainer><p className="muted">{t("selected")}: {profile.tenure_months} months · ₹{money(profile.loan_amount)} at {profile.rate}%</p></div></section>
      <p className="report-footer muted">{t("print")}</p>
    </>}
  </main><Footer/>
    <Dialog open={Boolean(selected)} onOpenChange={(open)=>{if(!open)setSelected(null);}}>{selected&&<DialogPortal><DialogOverlay className="drawer-backdrop"/><DialogContent className="drawer" aria-describedby="criteria-description"><div className="drawer-header"><div><span className="small-label">{selected.type==="NBFC"?t("nbfc"):t("bank")}</span><DialogTitle id="criteria-title">{selected.name}</DialogTitle></div><DialogClose asChild><button type="button" className="drawer-close" aria-label={t("close")}><X/></button></DialogClose></div><DialogDescription id="criteria-description" className="muted">{selected.product} · {statusText(selected.status)}</DialogDescription>
      <ul className="criterion-list">{selected.rules.map((rule)=>{const Icon=rule.status==="pass"?Check:rule.status==="warn"?TriangleAlert:CircleX;return <li key={rule.key}><span className="criterion-status"><Icon size={18}/></span><span><strong>{app(`rule_${rule.key}`)}</strong><br/><span className="muted">{t("yourValue")}: {requirementText(rule.user_value)} · {t("rule")}: {requirementText(rule.requirement)}</span>{rule.reliability&&<span className="rule-note"><span className="tag">{rule.reliability==="official"?t("official"):t("typical")}</span> {rule.note}</span>}{rule.needs_review&&<span className="rule-note"><span className="tag warning">{t("underReview")}</span></span>}</span>{rule.source&&<a className="inline-link" href={rule.source} target="_blank" rel="noreferrer">{t("source")}</a>}</li>})}</ul>
      {selected.fixes.length>0&&<><h3>{t("whyThis")}</h3><ul>{selected.fixes.map((fix)=><li key={fix}>{fix}</li>)}</ul></>}{selected.official_page&&<a className="inline-link" href={selected.official_page} target="_blank" rel="noreferrer">{t("source")}</a>}</DialogContent></DialogPortal>}</Dialog>
    <Dialog open={planner} onOpenChange={setPlanner}>{planner&&<DialogPortal><DialogOverlay className="drawer-backdrop"/><DialogContent className="drawer" aria-describedby="planner-description"><div className="drawer-header"><DialogTitle id="planner-title">{t("openWhatIf")}</DialogTitle><DialogClose asChild><button type="button" className="drawer-close" aria-label={t("close")}><X/></button></DialogClose></div><DialogDescription id="planner-description" className="muted">{t("change")}</DialogDescription>
      {[{field:"loan_amount" as const,min:50000,max:1000000,step:10000,label:t("loan")},{field:"existing_emi" as const,min:0,max:50000,step:500,label:t("existing")},{field:"revol_util" as const,min:0,max:100,step:5,label:t("cardUsage")},{field:"tenure_months" as const,min:12,max:60,step:12,label:t("tenure")}].map(item=><div className="slider-row" key={item.field}><label htmlFor={item.field}><span>{item.label}</span><strong>{item.field==="loan_amount"||item.field==="existing_emi"?`₹${money(whatValues[item.field])}`:item.field==="revol_util"?`${whatValues[item.field]}%`:`${whatValues[item.field]}m`}</strong></label><input id={item.field} type="range" min={item.min} max={item.max} step={item.step} value={whatValues[item.field]} onChange={event=>updateWhat(item.field,Number(event.target.value))}/></div>)}
      <article className="light-card"><h3>{t("update")}</h3>{whatLoading?<p>{t("saving")}</p>:whatResult?<><div className="big-number" style={{fontSize:34}}>{t(`band_${whatResult.readiness_band}`)}</div><p>{t("risk")}: {(whatResult.probability*100).toFixed(1)}% · {whatResult.delta.risk===0?"0.0":`${whatResult.delta.risk>0?"+":""}${(whatResult.delta.risk*100).toFixed(1)}`} pp</p><p>{t("meetCount",{count:whatBanks??0,total:lenders?.total??6})}</p></>:<p className="muted">{t("change")}</p>}</article>
    </DialogContent></DialogPortal>}</Dialog>
  </div>;
}
