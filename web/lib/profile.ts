export type Profile = {
  age: number; employment: "Salaried" | "Self-employed"; job_years: number; annual_income: number;
  existing_emi: number; card_bill: number; revol_util: number; open_acc: number; total_acc: number;
  mort_acc: number; pub_rec: number; bankruptcies: number; cibil_index: number; cibil: string;
  cibil_unknown: boolean; credit_year: number; credit_unknown: boolean; home: "rented" | "own" | "own_loan";
  loan_amount: number; tenure_months: number; purpose: string; rate: number; language: "en" | "hi";
};

export const sampleProfile: Profile = {
  age: 30, employment: "Salaried", job_years: 5, annual_income: 800000, existing_emi: 4844,
  card_bill: 12000, revol_util: 30, open_acc: 3, total_acc: 8, mort_acc: 0, pub_rec: 0,
  bankruptcies: 0, cibil_index: 1, cibil: "Good · 700–749", cibil_unknown: false,
  credit_year: 2015, credit_unknown: false, home: "rented", loan_amount: 300000,
  tenure_months: 36, purpose: "other", rate: 11, language: "en",
};

export function loadProfile(): Profile {
  if (typeof window === "undefined") return sampleProfile;
  try {
    const saved = sessionStorage.getItem("kreditly-profile");
    return saved ? { ...sampleProfile, ...JSON.parse(saved) } : sampleProfile;
  } catch { return sampleProfile; }
}

export function storeProfile(profile: Profile) {
  sessionStorage.setItem("kreditly-profile", JSON.stringify(profile));
}

export function money(value: number) {
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 }).format(value || 0);
}

export const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
