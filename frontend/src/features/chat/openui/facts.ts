import type { FactKind } from "../../../components/FactValue";

/** Properties the backend keeps for an expanded entity (`KEY_PROPERTIES` in app/agent/explore.py). */
export const EXPLORED_FIELDS = [
  "funding_stage",
  "founding_date",
  "total_funding",
  "employee_count_range",
  "headquarters_address",
  "operational_status",
  "website",
  "round_label",
  "round_type",
  "instrument",
  "transaction_value",
  "event_date",
  "announcement_date",
] as const;

const LABEL: Record<string, string> = {
  funding_stage: "Stage",
  founding_date: "Founded",
  total_funding: "Total raised",
  employee_count_range: "Team size",
  headquarters_address: "Headquarters",
  operational_status: "Status",
  website: "Website",
  round_label: "Round",
  round_type: "Round type",
  instrument: "Instrument",
  transaction_value: "Amount",
  event_date: "Date",
  announcement_date: "Announced",
  valid_since: "Since",
  valid_until: "Until",
};

export function factLabel(key: string): string {
  return LABEL[key] ?? key.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());
}

export function factKind(key: string): FactKind {
  return /(_date|^valid_)/.test(key) ? "date" : "auto";
}
