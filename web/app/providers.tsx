"use client";

import { NextIntlClientProvider } from "next-intl";
import { createContext, useContext, useEffect, useState } from "react";
import en from "../messages/en.json";
import hi from "../messages/hi.json";

type Language = "en" | "hi";
const LanguageContext = createContext<{ language: Language; toggle: () => void }>({ language: "en", toggle: () => {} });

export function useLanguage() { return useContext(LanguageContext); }

export function Providers({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<Language>("en");
  useEffect(() => {
    const saved = localStorage.getItem("kreditly-language");
    if (saved === "hi") setLanguage("hi");
  }, []);
  useEffect(() => { document.documentElement.lang = language; }, [language]);
  const toggle = () => setLanguage((old) => {
    const next = old === "en" ? "hi" : "en";
    localStorage.setItem("kreditly-language", next);
    return next;
  });
  return <LanguageContext.Provider value={{ language, toggle }}>
    <NextIntlClientProvider locale={language} messages={language === "hi" ? hi : en}>{children}</NextIntlClientProvider>
  </LanguageContext.Provider>;
}
