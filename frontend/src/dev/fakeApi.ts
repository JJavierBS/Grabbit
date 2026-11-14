// Dev-only stand-in for the FastAPI backend, on when VITE_FAKE_API=1. It replays the demo
// path on synthetic fixtures: a correction rewrites the profile and the report, undo goes
// back one version. The real backend replaces it once #21 serves the fixture endpoints.
import type { Alert, ChatMessage, Profile, ProfileChange, Report } from '../api/types';
import { chatV2, historyV2, profileV2, reportV1, reportV2, reportV3 } from './fixtures';

interface Version {
  profile: Profile;
  report: Report;
  history: ProfileChange[];
}

interface Script {
  match: RegExp;
  reply: string;
  next?: (v: Version) => Version;
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
  const before = field === 'instructions' ? v.profile.instructions : undefined;
  const profile: Profile = {
    ...v.profile,
    version,
    instructions: field === 'instructions' ? String(after) : v.profile.instructions,
    updated_at: now(),
  };
  const entry: ProfileChange = {
    version,
    field,
    before: before ?? null,
    after,
    reason,
    by: 'agent',
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
    reply: 'From now on: shorter reports, co-investors first. I rewrote your report.',
    next: (v) =>
      change(
        v,
        'instructions',
        'Short. Co-investors first. Two lines per startup. Plain language.',
        'You asked for shorter reports with co-investors first.',
        reportV2,
      ),
  },
  {
    match: /health|consumer|b2c/i,
    reply: 'From now on: no consumer health. Saltmarsh Bio is out of the report.',
    next: (v) =>
      change(
        v,
        'filters.sectors_out',
        ['Health', 'Consumer'],
        'You asked to drop consumer health.',
        reportV3,
      ),
  },
  {
    match: /confirm|looks right|keep me posted/i,
    reply:
      'Done. During Slush week I will send a daily digest, and I will alert you at once when something changes on your shortlist.',
  },
];

const fallback =
  'Noted. You can tell me how to change the report, for example "shorter, co-investors first".';

const state = {
  versions: [{ profile: profileV2, report: reportV1, history: historyV2 }] as Version[],
  chat: [...chatV2] as ChatMessage[],
  alerts: [] as Alert[],
};
const current = () => state.versions[state.versions.length - 1];

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

export async function fakeTransport(path: string, init?: RequestInit): Promise<Response> {
  const method = init?.method ?? 'GET';
  const body = init?.body ? JSON.parse(String(init.body)) : undefined;
  await delay(method === 'GET' ? 150 : 900);

  if (method === 'GET') {
    if (path === '/api/health') return json({ status: 'ok', cala_mode: 'fake', llm_mode: 'fake' });
    if (path === '/api/profile') return json(current().profile);
    if (path === '/api/profile/history') return json(current().history);
    if (path === '/api/chat') return json(state.chat);
    if (path === '/api/reports/latest') return json(current().report);
    if (path === '/api/alerts') return json(state.alerts);
  }
  if (method === 'POST' && path === '/api/chat') {
    const text = String(body?.text ?? '').trim();
    if (!text)
      return json({ error: { code: 'empty_message', message: 'Write a message first.' } }, 422);
    state.chat.push({
      id: `u${state.chat.length}`,
      role: 'user',
      text,
      created_at: now(),
      profile_changes: [],
    });
    const script = scripts.find((s) => s.match.test(text));
    const before = current();
    if (script?.next) state.versions.push(script.next(before));
    const after = current();
    const reply: ChatMessage = {
      id: `a${state.chat.length}`,
      role: 'agent',
      text: script?.reply ?? fallback,
      created_at: now(),
      profile_changes: after === before ? [] : [after.history[0]],
      report_id: after === before ? undefined : after.report.id,
    };
    state.chat.push(reply);
    return json(reply);
  }
  if (method === 'POST' && path === '/api/profile/undo') {
    if (state.versions.length === 1) {
      return json(
        { error: { code: 'nothing_to_undo', message: 'There is no change to undo.' } },
        409,
      );
    }
    state.versions.pop();
    state.chat.push({
      id: `a${state.chat.length}`,
      role: 'agent',
      text: 'Undone. I went back to the previous version of your report.',
      created_at: now(),
      profile_changes: [],
    });
    return json(current().profile);
  }
  if (method === 'POST' && path === '/api/reports/run') {
    const v = current();
    v.report = { ...v.report, id: `${v.report.id}-run${Date.now()}`, created_at: now() };
    return json(v.report);
  }
  return json(
    { error: { code: 'not_found', message: `${method} ${path} is not in the fake API.` } },
    404,
  );
}
