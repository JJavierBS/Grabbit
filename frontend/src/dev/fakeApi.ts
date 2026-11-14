// In-browser stand-in for the FastAPI backend. `npm run dev:fake` serves the whole demo path
// from it (VITE_FAKE_API=1), and the guided demo (#184) runs a fresh instance with its own
// script, so the visitor's real workspace is never touched.
import type {
  AgentQuestion,
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

export interface Version {
  profile: Profile;
  report: Report | null;
  history: ProfileChange[];
}

export interface Script {
  /** A pattern on the message, or a test that also sees how many messages the user sent before. */
  match: RegExp | ((text: string, turn: number) => boolean);
  reply: string;
  next?: (v: Version) => Version;
  questions?: AgentQuestion[];
  /** Delivers the simulated alert shortly after this reply, like the watcher would. */
  alert?: boolean;
  ui?: string;
  graph?: ExploredGraph;
  walk?: WalkSummary;
}

export interface FakeApiOptions {
  start: Version;
  chat?: ChatMessage[];
  scripts: Script[];
  fallback: string;
  /** Milliseconds before a GET and a POST answer. */
  latency?: { get: number; post: number };
  /** Milliseconds between a simulated event and its alert on the event stream. */
  alertDelay?: number;
}

type Listener = (ev: MessageEvent) => void;

/** Stands in for EventSource; the fake API pushes events to every open stream. */
export class FakeEventStream {
  readyState = 0;
  onopen: ((ev: Event) => unknown) | null = null;
  onerror: ((ev: Event) => unknown) | null = null;
  private listeners = new Map<string, Listener[]>();
  readonly url: string;
  private readonly streams: Set<FakeEventStream>;

  constructor(url: string, streams: Set<FakeEventStream>) {
    this.url = url;
    this.streams = streams;
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
    this.streams.delete(this);
  }
}

const now = () => new Date().toISOString();

/** One profile change, as the agent would record it, with the report it produced. */
export function change(
  v: Version,
  field: string,
  after: unknown,
  reason: string,
  report: Report | null,
  before: unknown = field === "instructions" ? v.profile.instructions : null,
): Version {
  const version = v.profile.version + 1;
  const profile: Profile = {
    ...v.profile,
    version,
    instructions: field === "instructions" ? String(after) : v.profile.instructions,
    updated_at: now(),
  };
  const entry: ProfileChange = { version, field, before, after, reason, by: "agent" };
  return {
    profile,
    report: report && { ...report, profile_version: version },
    history: [entry, ...v.history],
  };
}

const message = (
  id: string,
  role: ChatMessage["role"],
  text: string,
  extra: Partial<ChatMessage> = {},
): ChatMessage => ({
  id,
  role,
  text,
  created_at: now(),
  profile_changes: [],
  report_id: null,
  ui: null,
  graph: null,
  walk: null,
  sources: [],
  questions: [],
  ...extra,
});

/** Synthetic simulated alert on Northwind Labs, delivered like the real watcher would. */
function northwindAlert(): Alert {
  const source = { name: "Arctic Startup Daily", rank: "press" as const };
  return {
    id: `al-${Date.now()}`,
    created_at: now(),
    entity_id: "c-northwind",
    entity_name: "Northwind Labs",
    kind: "new_round",
    title: "Northwind Labs is raising a Series A",
    why_it_matters:
      "Aurora Ventures, one of your reference investors, leads it, and Northwind Labs is on your shortlist. It may close before you meet them at Slush.",
    importance: 0.9,
    facts: [
      {
        value: 8_000_000,
        unit: "EUR",
        trust: "press",
        sources: [
          { ...source, url: "https://example.com/press", date: null, date_precision: null },
        ],
      },
      {
        value: "2026-11-14",
        trust: "press",
        unit: null,
        sources: [{ ...source, url: null, date: "2026-11-14", date_precision: "day" }],
      },
    ],
    simulated: true,
  };
}

/** A self-contained fake backend: its own state, transport and event streams. */
export function createFakeApi(options: FakeApiOptions) {
  const latency = options.latency ?? { get: 150, post: 900 };
  const alertDelay = options.alertDelay ?? 1500;
  const state = {
    versions: [options.start],
    chat: [...(options.chat ?? [])],
    alerts: [] as Alert[],
    // Every report written, oldest first; GET /api/reports serves it newest first.
    reports: options.start.report ? [options.start.report] : ([] as Report[]),
  };
  const streams = new Set<FakeEventStream>();
  const timers = new Set<ReturnType<typeof setTimeout>>();
  const later = (ms: number, run: () => void) => {
    const t = setTimeout(() => {
      timers.delete(t);
      run();
    }, ms);
    timers.add(t);
  };

  const logReport = (r: Report | null) => {
    if (r && !state.reports.some((x) => x.id === r.id && x.profile_version === r.profile_version))
      state.reports.push(r);
  };
  const current = () => state.versions[state.versions.length - 1];
  const broadcast = (type: string, data: unknown) => {
    for (const s of streams) s.emit(type, data);
  };

  const json = (body: unknown, status = 200) =>
    new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
  const wait = (ms: number) => new Promise((r) => setTimeout(r, ms));

  // The fixture name only selects a scripted change in the real backend; the fake has one.
  function simulateAlert(_fixture?: string): Alert {
    const alert = northwindAlert();
    state.alerts.unshift(alert);
    later(alertDelay, () => broadcast("alert", alert));
    return alert;
  }

  function reply(text: string): ChatMessage {
    const turn = state.chat.filter((m) => m.role === "user").length;
    state.chat.push(message(`u${state.chat.length}`, "user", text));
    const script = options.scripts.find((s) =>
      s.match instanceof RegExp ? s.match.test(text) : s.match(text, turn),
    );
    const before = current();
    if (script?.next) {
      state.versions.push(script.next(before));
      logReport(current().report);
    }
    const after = current();
    const changed = after !== before;
    const answer = message(`a${state.chat.length}`, "agent", script?.reply ?? options.fallback, {
      profile_changes: changed ? [after.history[0]] : [],
      report_id: changed && after.report !== before.report ? (after.report?.id ?? null) : null,
      ui: script?.ui ?? null,
      graph: script?.graph ?? null,
      walk: script?.walk ?? null,
      questions: script?.questions ?? [],
    });
    state.chat.push(answer);
    if (script?.alert) simulateAlert();
    return answer;
  }

  async function transport(request: Request): Promise<Response> {
    const { method } = request;
    const path = new URL(request.url).pathname;
    const text = await request.text();
    // Talk sends audio, every other call JSON.
    const body =
      text && request.headers.get("content-type")?.startsWith("audio/")
        ? text
        : text
          ? JSON.parse(text)
          : undefined;
    await wait(method === "GET" ? latency.get : latency.post);

    if (method === "GET") {
      if (path === "/api/health")
        return json({ status: "ok", cala_mode: "fake", llm_mode: "fake" });
      if (path === "/api/profile") return json(current().profile);
      if (path === "/api/profile/history") return json(current().history);
      if (path === "/api/chat") return json(state.chat);
      if (path === "/api/reports/latest") {
        const report = current().report;
        return report
          ? json(report)
          : json({ error: { code: "no_report", message: "No report yet." } }, 404);
      }
      if (path === "/api/reports") return json([...state.reports].reverse().slice(0, 20));
      if (path === "/api/alerts") return json(state.alerts);
    }
    if (method === "POST" && path === "/api/transcribe")
      return json({ text: "Drop consumer health" });
    if (method === "POST" && path === "/api/chat") {
      const message = String(body?.text ?? "").trim();
      if (!message)
        return json({ error: { code: "empty_message", message: "Write a message first." } }, 422);
      return json(reply(message));
    }
    if (method === "POST" && path === "/api/profile/undo") {
      if (state.versions.length === 1) {
        return json(
          { error: { code: "nothing_to_undo", message: "There is no change to undo." } },
          409,
        );
      }
      state.versions.pop();
      state.chat.push(
        message(
          `a${state.chat.length}`,
          "agent",
          "Undone. I went back to the previous version of your report.",
        ),
      );
      return json(current().profile);
    }
    if (method === "POST" && path === "/api/demo/simulate-event") {
      return json(simulateAlert(String(body?.fixture ?? "new_round")));
    }
    if (method === "POST" && path === "/api/reports/run") {
      const v = current();
      if (!v.report)
        return json({ error: { code: "no_report", message: "No report to run yet." } }, 404);
      v.report = { ...v.report, id: `${v.report.id}-run${Date.now()}`, created_at: now() };
      logReport(v.report);
      return json(v.report);
    }
    return json(
      { error: { code: "not_found", message: `${method} ${path} is not in the fake API.` } },
      404,
    );
  }

  return {
    transport,
    openStream: (url: string) => new FakeEventStream(url, streams),
    simulateAlert,
    /** Stops pending alerts and closes every stream, so a finished demo leaves nothing behind. */
    dispose() {
      for (const t of timers) clearTimeout(t);
      timers.clear();
      for (const s of [...streams]) s.close();
    },
  };
}

export type FakeApi = ReturnType<typeof createFakeApi>;

/** The `dev:fake` path: a chat that already has its first report, ready for corrections. */
export const devFakeApi = (): FakeApi =>
  createFakeApi({
    start: { profile: profileV2, report: reportV1, history: historyV2 },
    chat: chatV2,
    fallback:
      'Noted. You can tell me how to change the report, for example "shorter, co-investors first".',
    scripts: [
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
    ],
  });
