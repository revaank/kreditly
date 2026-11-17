"use client";

import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Footer } from "../../components/footer";
import { Header } from "../../components/header";

type Summary = {
  best_model:string; dataset:{rows:number;target_counts:Record<string,number>;years:number[]};
  calibration:{method:string;validation_brier_before:number;validation_brier_after:number;test_brier_before:number;test_brier_after:number;shap_note:string};
  comparison:{model:string;validation_roc_auc:number;test_at_0_50:{accuracy:number;precision:number;recall:number;f1:number;roc_auc:number}}[];
  curves:Record<string,number>[]; confusion_matrix:number[][]; confusion_matrix_labels:string[];
  feature_importance:{feature:string;mean_absolute_shap:number;rank:number}[];
  data_sources:{name:string;url:string|null;rule_sources:string[]}[];
  review_sources:{name:string;url:string}[];
};

const names:Record<string,string>={term:"Repayment term",loan_to_income:"Loan / yearly income",revol_util:"Card limit used",dti:"Reported debt-to-income",open_acc:"Open accounts",revol_bal_to_income:"Card balance / yearly income",home_ownership:"Home ownership",mort_acc:"Mortgage accounts",total_acc:"Total credit accounts",purpose:"Loan purpose",pub_rec:"Public records",emp_length:"Employment length",credit_history_years:"Credit history length",pub_rec_bankruptcies:"Bankruptcy records"};
const colors=["#1F7A4D","#6B7880","#C39337"];

export default function ModelPage() {
  const t=useTranslations("model"); const app=useTranslations("app"); const [data,setData]=useState<Summary|null>(null);
  useEffect(()=>{fetch("/model-summary.json").then(r=>r.json()).then(setData).catch(()=>setData(null));},[]);
  return <div className="page-shell"><Header/><main className="container"><div className="page-top"><span className="pill">{app("reviewModel")}</span><h1>{t("title")}</h1><p className="section-intro">{t("subtitle")}</p></div>
    {!data?<div className="loading-card"><div className="skeleton large"/></div>:<>
      <section className="section model-section"><h2>{t("metrics")}</h2><div className="metric-grid"><article className="white-card"><span className="small-label">{app("bestValidation")}</span><h3>{data.best_model}</h3><p>{data.dataset.rows.toLocaleString("en-IN")} {t("rows")}</p></article><article className="white-card"><span className="small-label">{t("calibration")}</span><h3>{t("brierBefore")}: {data.calibration.test_brier_before.toFixed(3)}</h3><p>{t("brierAfter")}: <strong>{data.calibration.test_brier_after.toFixed(3)}</strong></p></article><article className="white-card"><span className="small-label">{app("targetOutcomes")}</span><div className="outcome-table">{Object.entries(data.dataset.target_counts).map(([label,count])=><div key={label}><span>{label==="Fully Paid"?app("outcomePaid"):app("outcomeCharged")}</span><strong>{count.toLocaleString("en-IN")}</strong></div>)}</div></article></div>
      <div className="section-heading-row" style={{marginTop:42}}><h2>{t("comparison")}</h2></div><div className="table-wrap"><table><thead><tr><th>{app("model")}</th><th>{app("validationAuc")}</th><th>{app("testAuc")}</th><th>{app("accuracy")}</th><th>{app("precision")}</th><th>{app("recall")}</th><th>{app("f1")}</th></tr></thead><tbody>{data.comparison.map(row=><tr key={row.model}><th>{row.model}</th><td>{row.validation_roc_auc.toFixed(3)}</td><td>{row.test_at_0_50.roc_auc.toFixed(3)}</td><td>{row.test_at_0_50.accuracy.toFixed(3)}</td><td>{row.test_at_0_50.precision.toFixed(3)}</td><td>{row.test_at_0_50.recall.toFixed(3)}</td><td>{row.test_at_0_50.f1.toFixed(3)}</td></tr>)}</tbody></table></div>
      </section>
      <section className="section model-section"><h2>{t("roc")}</h2><div className="chart-card"><ResponsiveContainer width="100%" height={330}><LineChart data={data.curves} margin={{top:8,right:16,left:0,bottom:4}}><CartesianGrid strokeDasharray="3 3" stroke="#E2E5DC"/><XAxis type="number" dataKey="XGBoost_fpr" domain={[0,1]} tickLine={false} axisLine={false} label={{value:app("falsePositive"),position:"insideBottom",offset:-2}}/><YAxis domain={[0,1]} tickLine={false} axisLine={false} label={{value:app("truePositive"),angle:-90,position:"insideLeft"}}/><Tooltip/><Legend/>{["Logistic Regression","Random Forest","XGBoost"].map((name,index)=><Line key={name} type="monotone" dataKey={`${name}_tpr`} name={name} stroke={colors[index]} dot={false} strokeWidth={2}/>)}</LineChart></ResponsiveContainer></div>
        <h2 style={{marginTop:42}}>{t("confusion")}</h2><div className="confusion-grid"><div/><div>{data.confusion_matrix_labels[0]}</div><div>{data.confusion_matrix_labels[1]}</div><strong>{data.confusion_matrix_labels[0]}</strong><span>{data.confusion_matrix[0][0].toLocaleString("en-IN")}</span><span>{data.confusion_matrix[0][1].toLocaleString("en-IN")}</span><strong>{data.confusion_matrix_labels[1]}</strong><span>{data.confusion_matrix[1][0].toLocaleString("en-IN")}</span><span>{data.confusion_matrix[1][1].toLocaleString("en-IN")}</span></div>
      </section>
      <section className="section model-section"><h2>{t("importance")}</h2><div className="importance-list">{data.feature_importance.map(item=><div className="importance-row" key={item.feature}><span>{names[item.feature]??item.feature}</span><div className="bar-track"><span style={{width:`${Math.max(2,item.mean_absolute_shap/data.feature_importance[0].mean_absolute_shap*100)}%`}}/></div><strong>{item.mean_absolute_shap.toFixed(3)}</strong></div>)}</div></section>
      <section className="section model-section"><h2>{t("limitations")}</h2><ul className="limitation-list"><li>{t("license")}</li><li>{t("usOnly")}</li><li>{t("historical")}</li><li>{t("shap")}</li><li>{app("timeLimitation")}</li></ul><details className="repro-details"><summary>{t("repro")}</summary><p>{app("reproModel",{method:data.calibration.method})}</p><p>{app("reproYears",{start:data.dataset.years[0],end:data.dataset.years[1],rows:data.dataset.rows.toLocaleString("en-IN")})}</p><p>{app("reproArtifacts")}</p></details></section>
      <section className="section model-section"><h2>{t("sources")}</h2><p>{t("sourceIntro")}</p><div className="source-list">{data.data_sources.map(item=><article className="white-card" key={item.name}><h3>{item.name}</h3>{item.url&&<a className="inline-link" href={item.url} target="_blank" rel="noreferrer">{item.url}</a>}{item.rule_sources.map(url=><div className="source-entry" key={url}><a className="inline-link" href={url} target="_blank" rel="noreferrer">{url}</a>{data.review_sources.some(source=>source.url===url)&&<span className="tag tag-review">{t("sourceUnderReview")}</span>}</div>)}</article>)}</div></section>
    </>}</main><Footer/></div>;
}
