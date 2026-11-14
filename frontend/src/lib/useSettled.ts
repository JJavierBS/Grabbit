import { useEffect, useState } from "react";

/** How long a "changed" highlight holds before it fades (#117). */
export const SETTLE_MS = 4000;

/**
 * False for `ms` after `key` changes, then true: lets a highlight point at what changed and
 * then step back. A null key never highlights, so it reads as settled.
 */
export function useSettled(key: unknown, ms = SETTLE_MS): boolean {
  const [settledKey, setSettledKey] = useState<unknown>(null);
  useEffect(() => {
    if (key === null || key === undefined) return;
    const timer = setTimeout(() => setSettledKey(key), ms);
    return () => clearTimeout(timer);
  }, [key, ms]);
  return key === null || key === undefined || settledKey === key;
}
