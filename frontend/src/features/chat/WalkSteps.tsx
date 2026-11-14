import { Brain, Network, RotateCcw, Search } from "lucide-react";
import type { WalkStep } from "../../api/types";
import styles from "./WalkSteps.module.css";

const ICONS = { search: Search, expand: Network, thought: Brain, rewrite: RotateCcw };

interface Props {
  steps: WalkStep[];
  /** Show only the newest this many and fold the rest into a count; all when unset. */
  visible?: number;
  label?: string;
}

/** The agent's Cala walk in plain words, one line per real step (#134, #138). */
export function WalkSteps({ steps, visible, label = "Steps" }: Props) {
  const hidden = visible ? Math.max(0, steps.length - visible) : 0;
  return (
    <ol className={styles.steps} aria-label={label}>
      {hidden > 0 && (
        <li className={styles.earlier}>
          {hidden} earlier step{hidden === 1 ? "" : "s"}
        </li>
      )}
      {steps.slice(hidden).map((s) => (
        <Step key={s.id} step={s} />
      ))}
    </ol>
  );
}

function Step({ step }: { step: WalkStep }) {
  const Icon = ICONS[step.kind];
  return (
    <li className={styles.step} data-kind={step.kind} data-done={step.done || undefined}>
      <Icon className={styles.icon} aria-hidden="true" />
      <span className={styles.text}>
        {step.kind === "thought" && <span className={styles.label}>Model's reasoning: </span>}
        {step.text}
        {!step.done && "…"}
        {step.result && <span className={styles.result}> → {step.result}</span>}
      </span>
    </li>
  );
}
