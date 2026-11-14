import { type RefObject, useEffect, useRef, useState } from "react";

/** Longest an exit may hold an element on screen, even if `finished` never settles. */
export const EXIT_FALLBACK_MS = 400;

/**
 * Resolves once the element's running animations end, at once when it has none (reduced
 * motion, or a browser without the Web Animations API), and never later than the fallback.
 */
export function afterExit(element: Element | null, onDone: () => void): () => void {
  let done = false;
  const finish = () => {
    if (done) return;
    done = true;
    onDone();
  };
  const running = element?.getAnimations?.() ?? [];
  if (running.length === 0) {
    finish();
    return () => undefined;
  }
  const timer = window.setTimeout(finish, EXIT_FALLBACK_MS);
  Promise.all(running.map((a) => a.finished)).then(finish, finish);
  return () => {
    done = true;
    window.clearTimeout(timer);
  };
}

/**
 * Keeps the last value on screen while its element plays its exit animation, so a panel can
 * slide out instead of vanishing. `leaving` is true from the moment `value` becomes null
 * until the exit ends; style the exit from `data-state="leaving"`.
 */
export function usePresence<T>(
  value: T | null,
  ref: RefObject<Element>,
): { shown: T | null; leaving: boolean } {
  const [shown, setShown] = useState<T | null>(value);
  const [leaving, setLeaving] = useState(false);
  const latest = useRef(value);
  latest.current = value;

  useEffect(() => {
    if (value !== null) {
      setShown(value);
      setLeaving(false);
      return;
    }
    setLeaving(true);
  }, [value]);

  // Wait for the exit animation that `data-state="leaving"` started, then unmount.
  useEffect(() => {
    if (!leaving) return;
    return afterExit(ref.current, () => {
      if (latest.current === null) {
        setShown(null);
        setLeaving(false);
      }
    });
  }, [leaving, ref]);

  return { shown: value ?? shown, leaving: value === null && shown !== null };
}
