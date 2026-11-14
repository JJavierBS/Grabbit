// shortcut: copied by hand from docs/agents/api.md "Shared types" because #21 has not
// generated src/api/schema.ts yet; once it exists, re-export these names from
// components['schemas'] and delete the hand-written shapes.

export type TrustLevel =
  | 'filing'
  | 'primary'
  | 'press'
  | 'aggregator'
  | 'web_unverified'
  | 'not_published';

export type DatePrecision = 'day' | 'month' | 'year';

export interface Source {
  name: string;
  url?: string | null;
  date?: string | null;
  date_precision?: DatePrecision | null;
  rank: TrustLevel;
}

export type FactScalar = string | number | boolean;

export interface Fact {
  value?: FactScalar | FactScalar[] | null;
  unit?: string | null;
  trust: TrustLevel;
  sources: Source[];
}

export interface Investor {
  entity_id: string;
  name: string;
  is_lead: boolean;
  role: 'investor' | 'lender';
}

export interface Round {
  entity_id: string;
  label?: string | null;
  name: string;
  amount: Fact;
  date: Fact;
  investors: Investor[];
}

export type SignalKind = 'co_invest' | 'lead_follow_on' | 'likely_to_raise';

export interface Signal {
  kind: SignalKind;
  label: string;
  value?: unknown;
  explanation: string;
  facts: Fact[];
}

export interface Candidate {
  entity_id: string;
  name: string;
  website?: string | null;
  description?: string | null;
  founding_date: Fact;
  funding_stage: Fact;
  headcount: Fact;
  total_funding: Fact;
  hq: Fact;
  industries: string[];
  rounds: Round[];
  signals: Signal[];
}

export interface Profile {
  version: number;
  event_id?: string | null;
  thesis: string;
  filters: {
    stages: string[];
    sectors_in: string[];
    sectors_out: string[];
    countries: string[];
    headcount_max?: number | null;
    ticket?: Fact | null;
  };
  reference_investors: { entity_id: string; name: string }[];
  style: {
    length: 'short' | 'medium' | 'long';
    detail: 'plain' | 'technical';
    language: string;
    sections: string[];
  };
  cadence: 'event' | 'daily' | 'weekly';
  alert_threshold: 'low' | 'medium' | 'high';
  instructions: string;
  updated_at: string;
}

export interface ProfileChange {
  version: number;
  field: string;
  before: unknown;
  after: unknown;
  reason: string;
  by: 'user' | 'agent';
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'agent';
  text: string;
  created_at: string;
  profile_changes: ProfileChange[];
  report_id?: string | null;
}

export interface ReportSection {
  title: string;
  body_md: string;
  candidate_ids: string[];
}

export interface Report {
  id: string;
  kind: 'prep' | 'digest' | 'memo';
  created_at: string;
  profile_version: number;
  summary: string;
  sections: ReportSection[];
  candidates: Candidate[];
}

export type AlertKind =
  | 'new_round'
  | 'executive_change'
  | 'headcount_jump'
  | 'acquisition'
  | 'status_change'
  | 'web_news';

export interface Alert {
  id: string;
  created_at: string;
  entity_id: string;
  entity_name: string;
  kind: AlertKind;
  title: string;
  why_it_matters: string;
  importance: number;
  facts: Fact[];
  simulated: boolean;
}

export interface ApiErrorBody {
  error: { code: string; message: string };
}
