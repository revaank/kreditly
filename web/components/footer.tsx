"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";

export function Footer() {
  const t = useTranslations("home");
  const app = useTranslations("app");
  return <footer className="site-footer"><div className="container footer-meta"><Link className="brand" href="/"><span className="brand-mark">K</span> kreditly</Link><span>© Kreditly</span></div><div className="container"><p>{t("disclaimer")}</p><p>{app("bankDisclaimer")}</p></div></footer>;
}
