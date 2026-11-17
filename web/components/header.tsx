"use client";

import { Menu, X } from "lucide-react";
import Link from "next/link";
import { useTranslations } from "next-intl";
import { useState } from "react";
import { useLanguage } from "../app/providers";

export function Header() {
  const t = useTranslations("nav");
  const app = useTranslations("app");
  const { toggle } = useLanguage();
  const [open, setOpen] = useState(false);
  return <header className="site-header"><Link className="brand" href="/" aria-label="Kreditly home"><span className="brand-mark">K</span> kreditly</Link>
    <button type="button" className="menu-button" aria-label={open ? app("menuClose") : app("menuOpen")} onClick={() => setOpen(!open)}>{open ? <X /> : <Menu />}</button>
    <nav className={open ? "nav-links nav-open" : "nav-links"} aria-label="Main navigation">
      <Link href="/#how" onClick={() => setOpen(false)}>{t("how")}</Link><Link href="/#lenders" onClick={() => setOpen(false)}>{t("lenders")}</Link>
      <Link href="/model" onClick={() => setOpen(false)}>{t("reviewers")}</Link>
      <button type="button" className="language-button" onClick={toggle} aria-label={t("toggle")}>{t("toggle")}</button>
      <Link className="nav-cta" href="/check" onClick={() => setOpen(false)}>{t("check")}</Link>
    </nav>
  </header>;
}
