const STORAGE_KEY = "grabbit.workspace";
const LIST_KEY = "grabbit.researches";
/** Longest title kept for a research; the sidebar clips it further. */
export const TITLE_CHARS = 80;

/** Used only when storage is blocked: the page keeps its researches until it reloads. */
let fallback: string | null = null;
let fallbackList: Research[] = [];

/** One thesis with its own chat, profile, reports and alerts: one anonymous workspace (#145). */
export interface Research {
  id: string;
  /** The first message sent in it; null until then. */
  title: string | null;
  created_at: string;
}

function newId(): string {
  if (typeof globalThis.crypto.randomUUID === "function") return globalThis.crypto.randomUUID();
  // randomUUID needs a secure context; the laptop demo can be opened over plain http.
  const bytes = globalThis.crypto.getRandomValues(new Uint8Array(16));
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}

/**
 * This browser's current anonymous workspace, created on first use. The backend keeps each
 * workspace's profile, chat, reports and alerts apart, so demo visitors never share state.
 */
export function workspaceId(): string {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    const id = newId();
    localStorage.setItem(STORAGE_KEY, id);
    return id;
  } catch {
    fallback ??= newId();
    return fallback;
  }
}

/** `url` with the workspace as a query parameter, for EventSource, which cannot send headers. */
export function withWorkspace(url: string): string {
  const separator = url.includes("?") ? "&" : "?";
  return `${url}${separator}workspace=${encodeURIComponent(workspaceId())}`;
}

function readList(): Research[] {
  try {
    const parsed = JSON.parse(localStorage.getItem(LIST_KEY) ?? "[]");
    return Array.isArray(parsed) ? parsed.filter((r) => typeof r?.id === "string") : [];
  } catch {
    return fallbackList;
  }
}

function writeList(list: Research[]) {
  try {
    localStorage.setItem(LIST_KEY, JSON.stringify(list));
  } catch {
    // Private mode or blocked storage: the list lives until the page reloads.
    fallbackList = list;
  }
}

function setCurrent(id: string) {
  try {
    localStorage.setItem(STORAGE_KEY, id);
  } catch {
    // As above: the current research lives until the page reloads.
    fallback = id;
  }
}

/** Every research of this browser, newest first; the current one is always in it. */
export function researches(): Research[] {
  const current = workspaceId();
  const list = readList();
  if (list.some((r) => r.id === current)) return list;
  // A workspace from before research lists existed, or the first visit.
  const known = [{ id: current, title: null, created_at: new Date().toISOString() }, ...list];
  writeList(known);
  return known;
}

const listeners = new Set<() => void>();
let snapshot: { current: string; list: Research[] } | null = null;

function changed() {
  snapshot = null;
  for (const listener of listeners) listener();
}

export function subscribeResearches(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/** A stable value for useSyncExternalStore: the same object until something changes. */
export function researchSnapshot(): { current: string; list: Research[] } {
  // Storage may have changed under us (another tab, cleared site data): follow it.
  if (!snapshot || snapshot.current !== workspaceId()) {
    snapshot = { current: workspaceId(), list: researches() };
  }
  return snapshot;
}

/**
 * Starts a fresh research and makes it current. A current research nobody wrote in yet is
 * reused instead, so pressing "New research" twice never leaves empty ones behind.
 */
export function startResearch(): string {
  const list = researches();
  const current = list.find((r) => r.id === workspaceId());
  if (current && !current.title) return current.id;
  const id = newId();
  writeList([{ id, title: null, created_at: new Date().toISOString() }, ...list]);
  setCurrent(id);
  changed();
  return id;
}

export function switchResearch(id: string) {
  if (id === workspaceId() || !researches().some((r) => r.id === id)) return;
  setCurrent(id);
  changed();
}

/** Names the current research after its first message; a named one keeps its name. */
export function nameResearch(text: string) {
  const title = text.trim().replace(/\s+/g, " ").slice(0, TITLE_CHARS);
  const id = workspaceId();
  const list = researches();
  const current = list.find((r) => r.id === id);
  if (!title || !current || current.title) return;
  writeList(list.map((r) => (r.id === id ? { ...r, title } : r)));
  changed();
}
