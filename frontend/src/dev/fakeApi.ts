// Dev-only stand-in for the FastAPI backend, on when VITE_FAKE_API=1. It replays the demo
// path on synthetic fixtures: a correction rewrites the profile and the report, undo goes
// back one version. The real backend replaces it once #21 serves the fixture endpoints.
import type {
  Alert,
  ChatMessage,
  ExploredGraph,
  Profile,
  ProfileChange,
  Report,
  WalkSummary,
} from "../api/types";
import {
  chatV2,
  exploredAnswerUi,
  exploredAurora,
  exploredAuroraWalk,
  historyV2,
  profileV2,
  reportV1,
  reportV2,
  reportV3,
} from "./fixtures";

interface Version {
  profile: Profile;
  report: Report;
  history: ProfileChange[];
}

interface Script {
  match: RegExp;
  reply: string;
  next?: (v: Version) => Version;
  ui?: string;
  graph?: ExploredGraph;
  walk?: WalkSummary;
}

const now = () => new Date().toISOString();

function change(
  v: Version,
  field: string,
  after: unknown,
  reason: string,
  report: Report,
): Version {
  const version = v.profile.version + 1;
  const before = field === "instructions" ? v.profile.instructions : undefined;
  const profile: Profile = {
    ...v.profile,
    version,
    instructions: field === "instructions" ? String(after) : v.profile.instructions,
    updated_at: now(),
  };
  const entry: ProfileChange = {
    version,
    field,
    before: before ?? null,
    after,
    reason,
    by: "agent",
  };
  return {
    profile,
    report: { ...report, profile_version: version },
    history: [entry, ...v.history],
  };
}

const scripts: Script[] = [
  {
    match: /short|co-?invest/i,
    reply: "From now on: shorter reports, co-investors first. I rewrote your report.",
    next: (v) =>
      change(
        v,
        "instructions",
        "Short. Co-investors first. Two lines per startup. Plain language.",
        "You asked for shorter reports with co-investors first.",
        reportV2,
      ),
  },
  {
    match: /health|consumer|b2c/i,
    reply: "From now on: no consumer health. Saltmarsh Bio is out of the report.",
    next: (v) =>
      change(
        v,
        "filters.sectors_out",
        ["Health", "Consumer"],
        "You asked to drop consumer health.",
        reportV3,
      ),
  },
  {
    match: /what else|backed|invested in/i,
    reply: "Aurora Ventures also led the seed of Fjordlight Robotics.",
    ui: exploredAnswerUi,
    graph: exploredAurora,
    walk: exploredAuroraWalk,
  },
  {
    match: /confirm|looks right|keep me posted/i,
    reply:
      "Done. During Slush week I will send a daily digest, and I will alert you at once when something changes on your shortlist.",
  },
];

const fallback =
  'Noted. You can tell me how to change the report, for example "shorter, co-investors first".';

const state = {
  versions: [{ profile: profileV2, report: reportV1, history: historyV2 }] as Version[],
  chat: [...chatV2] as ChatMessage[],
  alerts: [] as Alert[],
  // Every report written, oldest first; GET /api/reports serves it newest first.
  reports: [reportV1] as Report[],
};
const logReport = (r: Report) => {
  if (!state.reports.some((x) => x.id === r.id && x.profile_version === r.profile_version))
    state.reports.push(r);
};
const current = () => state.versions[state.versions.length - 1];

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

export async function fakeTransport(request: Request): Promise<Response> {
  const { method } = request;
  const path = new URL(request.url).pathname;
  const text = await request.text();
  const body = text ? JSON.parse(text) : undefined;
  await delay(method === "GET" ? 150 : 900);

  if (method === "GET") {
    if (path === "/api/health") return json({ status: "ok", cala_mode: "fake", llm_mode: "fake" });
    if (path === "/api/profile") return json(current().profile);
    if (path === "/api/profile/history") return json(current().history);
    if (path === "/api/chat") return json(state.chat);
    if (path === "/api/reports/latest") return json(current().report);
    if (path === "/api/reports") return json([...state.reports].reverse().slice(0, 20));
    if (path === "/api/alerts") return json(state.alerts);
  }
  if (method === "POST" && path === "/api/chat") {
    const text = String(body?.text ?? "").trim();
    if (!text)
      return json({ error: { code: "empty_message", message: "Write a message first." } }, 422);
    state.chat.push({
      id: `u${state.chat.length}`,
      role: "user",
      report_id: null,
      ui: null,
      graph: null,
      walk: null,
      sources: [],
      questions: [],
      text,
      created_at: now(),
      profile_changes: [],
    });
    const script = scripts.find((s) => s.match.test(text));
    const before = current();
    if (script?.next) {
      state.versions.push(script.next(before));
      logReport(current().report);
    }
    const after = current();
    const reply: ChatMessage = {
      id: `a${state.chat.length}`,
      role: "agent",
      text: script?.reply ?? fallback,
      created_at: now(),
      profile_changes: after === before ? [] : [after.history[0]],
      report_id: after === before ? null : after.report.id,
      ui: script?.ui ?? null,
      graph: script?.graph ?? null,
      walk: script?.walk ?? null,
      sources: [],
      questions: [],
    };
    state.chat.push(reply);
    return json(reply);
  }
  if (method === "POST" && path === "/api/profile/undo") {
    if (state.versions.length === 1) {
      return json(
        { error: { code: "nothing_to_undo", message: "There is no change to undo." } },
        409,
      );
    }
    state.versions.pop();
    state.chat.push({
      id: `a${state.chat.length}`,
      role: "agent",
      report_id: null,
      ui: null,
      graph: null,
      walk: null,
      sources: [],
      questions: [],
      text: "Undone. I went back to the previous version of your report.",
      created_at: now(),
      profile_changes: [],
    });
    return json(current().profile);
  }
  if (method === "POST" && path === "/api/demo/simulate-event") {
    return json(simulateAlert(String(body?.fixture ?? "new_round")));
  }
  if (method === "POST" && path === "/api/reports/run") {
    const v = current();
    v.report = { ...v.report, id: `${v.report.id}-run${Date.now()}`, created_at: now() };
    logReport(v.report);
    return json(v.report);
  }
  return json(
    { error: { code: "not_found", message: `${method} ${path} is not in the fake API.` } },
    404,
  );
}

// ---- Event stream (/api/events) ------------------------------------------------------

type Listener = (ev: MessageEvent) => void;
const streams = new Set<FakeEventStream>();

/** Stands in for EventSource; the fake API pushes events to every open stream. */
export class FakeEventStream {
  readyState = 0;
  onopen: ((ev: Event) => unknown) | null = null;
  onerror: ((ev: Event) => unknown) | null = null;
  private listeners = new Map<string, Listener[]>();
  readonly url: string;

  constructor(url: string) {
    this.url = url;
    streams.add(this);
    setTimeout(() => {
      this.readyState = 1;
      this.onopen?.(new Event("open"));
    }, 50);
  }

  addEventListener(type: string, listener: Listener) {
    this.listeners.set(type, [...(this.listeners.get(type) ?? []), listener]);
  }

  emit(type: string, data: unknown) {
    const ev = new MessageEvent(type, { data: JSON.stringify(data) });
    for (const l of this.listeners.get(type) ?? []) l(ev);
  }

  close() {
    this.readyState = 2;
    streams.delete(this);
  }
}

const broadcast = (type: string, data: unknown) => {
  for (const s of streams) s.emit(type, data);
};

/** Synthetic simulated alert on Northwind Labs, delivered like the real watcher would. */
// The fixture name only selects a scripted change in the real backend; the fake has one.
export function simulateAlert(_fixture: string): Alert {
  const alert: Alert = {
    id: `al-${Date.now()}`,
    created_at: now(),
    entity_id: "c-northwind",
    entity_name: "Northwind Labs",
    kind: "new_round",
    title: "Northwind Labs is raising a Series A",
    why_it_matters: `Aurora Ventures, one of your reference investors, leads it, and Northwind Labs is on your shortlist. It may close before you meet them at Slush.`,
    importance: 0.9,
    facts: [
      {
        value: 8_000_000,
        unit: "EUR",
        trust: "press",
        sources: [
          {
            name: "Arctic Startup Daily",
            url: "https://example.com/press",
            date: null,
            date_precision: null,
            rank: "press",
          },
        ],
      },
      {
        value: "2026-11-14",
        trust: "press",
        unit: null,
        sources: [
          {
            name: "Arctic Startup Daily",
            url: null,
            date: "2026-11-14",
            date_precision: "day",
            rank: "press",
          },
        ],
      },
    ],
    simulated: true,
  };
  state.alerts.unshift(alert);
  setTimeout(() => broadcast("alert", alert), 1500);
  return alert;
}
