import type { WalkSummary } from "../../api/types";
import styles from "./HowIFound.module.css";
import { WalkSteps } from "./WalkSteps";

export function summaryText(walk: WalkSummary): string {
  const time = walk.seconds < 1 ? "under a second" : `${Math.round(walk.seconds)} s`;
  const what =
    walk.checked === 1
      ? "1 company, person or round"
      : `${walk.checked} companies, people and rounds`;
  return `Checked ${what} in Cala in ${time}`;
}

/**
 * How the agent found an answer in Cala, kept folded on it once the live walk is gone (#138).
 * The guided demo opens it: the steps are part of what it teaches (#184).
 */
export function HowIFound({ walk, open = false }: { walk: WalkSummary; open?: boolean }) {
  return (
    <details className={styles.how} open={open}>
      <summary className={styles.summary}>
        <span className={styles.lead}>How I found this</span> · {summaryText(walk)}
      </summary>
      <WalkSteps steps={walk.steps} label="How I found this, step by step" />
    </details>
  );
}
