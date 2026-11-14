const STORAGE_KEY = "grabbit.workspace";

/** Used only when storage is blocked: the page keeps one workspace until it reloads. */
let fallback: string | null = null;

function newId(): string {
  if (typeof globalThis.crypto.randomUUID === "function") return globalThis.crypto.randomUUID();
  // randomUUID needs a secure context; the laptop demo can be opened over plain http.
  const bytes = globalThis.crypto.getRandomValues(new Uint8Array(16));
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}

/**
 * This browser's anonymous workspace, created on first use. The backend keeps each
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
