import { type RefObject, useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import type { ChatMessage } from "../../api/types";

/** Within this distance of the end, the reader counts as following the conversation. */
const NEAR_END_PX = 48;

const behavior = (): ScrollBehavior =>
  window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";

interface FollowLog {
  logRef: RefObject<HTMLDivElement>;
  onScroll: () => void;
  /** A reply arrived while the reader was scrolled up. */
  behind: boolean;
  jumpToLatest: () => void;
  /** Messages that arrived during this visit, which enter with a short fade. */
  isNew: (message: ChatMessage) => boolean;
}

/**
 * Follows the chat like claude.ai: the history opens at its end; the reader's own message
 * scrolls into view; a reply scrolls to its first line only if the reader was already at the
 * end, otherwise a "Jump to latest" pill offers it. `extra` is anything else appended to the
 * log (a card, the working line) that should be followed the same way.
 */
export function useFollowLog(messages: ChatMessage[], ready: boolean, extra: unknown): FollowLog {
  const logRef = useRef<HTMLDivElement>(null);
  const following = useRef(true);
  const [behind, setBehind] = useState(false);
  const known = useRef<Set<string> | null>(null);
  const lastId = useRef<string | undefined>(undefined);

  const toEnd = useCallback((how: ScrollBehavior) => {
    const log = logRef.current;
    if (!log) return;
    log.scrollTo?.({ top: log.scrollHeight, behavior: how });
    following.current = true;
    setBehind(false);
  }, []);

  // The stored conversation opens at its end, without animating what was already there.
  useLayoutEffect(() => {
    if (!ready || known.current) return;
    known.current = new Set(messages.map((m) => m.id));
    lastId.current = messages.at(-1)?.id;
    toEnd("auto");
  }, [ready, messages, toEnd]);

  // biome-ignore lint/correctness/useExhaustiveDependencies: react to a new last message only.
  useEffect(() => {
    if (!known.current) return;
    const last = messages.at(-1);
    if (!last || last.id === lastId.current) return;
    lastId.current = last.id;
    if (last.role === "user") {
      toEnd(behavior());
      return;
    }
    if (!following.current) {
      setBehind(true);
      return;
    }
    const node = logRef.current?.querySelector(`[data-message-id="${CSS.escape(last.id)}"]`);
    node?.scrollIntoView?.({ block: "start", behavior: behavior() });
  }, [messages]);

  // A card or the working line appended under the messages: keep it in view if following.
  // biome-ignore lint/correctness/useExhaustiveDependencies: follow changes of the extra content.
  useEffect(() => {
    if (known.current && following.current) toEnd(behavior());
  }, [extra]);

  const onScroll = useCallback(() => {
    const log = logRef.current;
    if (!log) return;
    following.current = log.scrollHeight - log.scrollTop - log.clientHeight <= NEAR_END_PX;
    if (following.current) setBehind(false);
  }, []);

  const isNew = useCallback(
    (message: ChatMessage) =>
      known.current !== null &&
      !known.current.has(message.id) &&
      // A sent message is shown at once as `pending-…`, then replaced by the stored copy;
      // only the first appearance enters.
      (message.role === "agent" || message.id.startsWith("pending-")),
    [],
  );

  return { logRef, onScroll, behind, jumpToLatest: () => toEnd(behavior()), isNew };
}
