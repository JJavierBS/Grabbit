import { useEffect, useState } from "react";
import styles from "./WorkingLine.module.css";

/** After this long the line also shows how long the turn has taken. */
export const ELAPSED_AFTER_MS = 10_000;

export function workingText(hasReport: boolean): string {
  return hasReport
    ? "Reading your message and checking the report…"
    : "Reading your thesis and walking the Slush attendees in Cala…";
}

interface WorkingLineProps {
  /** With no report yet, the agent is walking Cala for the first one. */
  hasReport: boolean;
}

/**
 * The agent's working state: the logo's speed lines pulse and a violet light sweeps the text.
 * A live turn can take minutes with Cala, so from 10 s it also counts the seconds. The count
 * is hidden from screen readers; they hear the sentence once, not every second.
 */
export function WorkingLine({ hasReport }: WorkingLineProps) {
  const [startedAt] = useState(() => Date.now());
  const [now, setNow] = useState(startedAt);

  useEffect(() => {
    const tick = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(tick);
  }, []);

  const elapsed = now - startedAt;
  return (
    <p className={styles.line} role="status">
      <span className={styles.speed} aria-hidden="true">
        <span />
        <span />
      </span>
      <span className={styles.text}>{workingText(hasReport)}</span>
      {elapsed >= ELAPSED_AFTER_MS && (
        <span className={styles.elapsed} aria-hidden="true">
          · {Math.floor(elapsed / 1000)} s
        </span>
      )}
    </p>
  );
}
