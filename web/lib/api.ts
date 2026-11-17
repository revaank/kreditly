import { apiBase, type Profile } from "./profile";

export async function apiRequest<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    method: body === undefined ? "GET" : "POST",
    headers: { "Content-Type": "application/json", "Accept-Language": "en" },
    body: body === undefined ? undefined : JSON.stringify(body),
    cache: "no-store",
  });
  if (!response.ok) throw new Error("Kreditly API request failed");
  return response.json() as Promise<T>;
}

export type Prediction = {
  probability: number; readiness_band: "good" | "fair" | "needs_work"; label: string;
  top_factors: { feature: string; helpful: boolean; contribution: number; text: string }[];
  suggestions: { field: string; value: number; risk_reduction: number; text: string }[];
  finance: { emi: number; total_interest: number; total_repayment: number; foir: number };
};

export type Lender = {
  id: string; name: string; short_name: string; type: string; product: string;
  status: "qualify" | "close" | "miss"; rules: {
    key: string; status: "pass" | "warn" | "fail"; user_value: unknown; requirement: unknown;
    reliability: string | null; note: string | null; source: string | null; needs_review: boolean;
  }[];
  interest_rate_from: number | null; official_page: string | null; fixes: string[];
};

export type LendersResponse = { lenders: Lender[]; qualify_count: number; total: number; disclaimer?: string; last_checked?: string };

export function profilePayload(profile: Profile, language: "en" | "hi") {
  return { ...profile, language };
}
