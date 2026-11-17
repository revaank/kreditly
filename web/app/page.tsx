"use client";

import { ArrowRight, Calculator, Check, ShieldCheck, SlidersHorizontal, Sparkles } from "lucide-react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { Footer } from "../components/footer";
import { Header } from "../components/header";
import { sampleProfile, storeProfile } from "../lib/profile";

export default function HomePage() {
  const t = useTranslations("home");
  const app = useTranslations("app");
  const preview = () => { storeProfile(sampleProfile); window.location.href = "/results"; };
  return <div className="page-shell"><Header /><main>
    <section className="container hero"><div>
      <span className="pill"><Sparkles size={15} />{t("pill")}</span>
      <h1>{t("title")}</h1><p className="hero-copy">{t("subtitle")}</p>
      <div className="button-row"><Link className="button button-lime" href="/check">{t("primary")} <ArrowRight size={17} /></Link><button type="button" className="button button-white" onClick={preview}>{t("example")}</button></div>
      <div className="trust-row"><span><Check size={16}/>{t("trust1")}</span><span><Check size={16}/>{t("trust2")}</span><span><Check size={16}/>{t("trust3")}</span></div>
    </div><section className="sample-panel" aria-label={t("sample")}>
      <div className="sample-head"><span>{t("sample")}</span><span className="band-chip">{app("sampleBand")}</span></div><div className="meter"><span /></div>
      <div className="sample-grid"><div className="sample-cell"><small>{app("sampleCriteria")}</small><strong>5 / 6</strong><small>{t("met")}</small></div><div className="sample-cell"><small>{t("emi")}</small><strong>₹9,822</strong><small>{app("sampleTerm")}</small></div></div>
      <div className="sample-fix"><small>{t("fix")}</small><p>{app("sampleSourceNote")}</p></div>
    </section></section>
    <section className="container trust-strip" id="lenders"><span>{t("lenderStrip")}</span><div className="lender-names"><span>SBI</span><span>HDFC Bank</span><span>ICICI</span><span>Axis Bank</span><span>Bajaj Finance</span><span>Tata Capital</span></div></section>
    <section className="container section" id="how"><h2>{t("howTitle")}</h2><div className="three-grid">
      {[1,2,3].map((n) => <article className="step-card" key={n}><span className="step-num">0{n}</span><h3>{t(`step${n}`)}</h3><p>{t(`step${n}Body`)}</p></article>)}
    </div></section>
    <section className="container dark-feature"><h2>{t("panelTitle")}</h2><div className="feature-grid">
      {[{icon:<ShieldCheck/>,title:"feat1",body:"feat1Body"},{icon:<Sparkles/>,title:"feat2",body:"feat2Body"},{icon:<SlidersHorizontal/>,title:"feat3",body:"feat3Body"},{icon:<Calculator/>,title:"feat4",body:"feat4Body"}].map((item) => <article className="feature-card" key={item.title}><span className="feature-icon">{item.icon}</span><h3>{t(item.title)}</h3><p>{t(item.body)}</p></article>)}
    </div></section>
  </main><Footer /></div>;
}
