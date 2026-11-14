import { workspaceId } from "../../api/workspace";

// A half-written message survives switching research and reloading (#188); storage may be
// unavailable, and then the draft only lives while the chat is open.
const key = () => `grabbit.draft:${workspaceId()}`;

export function readDraft(): string {
  try {
    return localStorage.getItem(key()) ?? "";
  } catch {
    return "";
  }
}

export function saveDraft(text: string) {
  try {
    if (text) localStorage.setItem(key(), text);
    else localStorage.removeItem(key());
  } catch {
    // Private mode or blocked storage: nothing to keep it in.
  }
}
