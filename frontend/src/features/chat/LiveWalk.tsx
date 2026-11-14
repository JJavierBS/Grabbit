import { Brain, Network, RotateCcw, Search } from "lucide-react";
import { useProfile } from "../../api/hooks/queries";
import type { WalkStep, WalkTrace } from "../../api/types";
import styles from "./LiveWalk.module.css";
import { ExploredGraphView } from "./openui/ExploredGraphView";
import { VisualAnswer } from "./openui/VisualAnswer";

/** Steps shown at once; older ones fold into a count so the graph stays in view. */
export const VISIBLE_STEPS = 5;

const ICONS = { search: Search, expand: Network, thought: Brain, rewrite: RotateCcw };

export function budgetText(trace: WalkTrace): string {
  const round = trace.round ? `Round ${trace.round} of ${trace.max_rounds} · ` : "";
  return `${round}${trace.nodes} of ${trace.max_nodes} Cala entities`;
}

/**
 * The agent's Cala walk while it happens (#134): the subgraph growing from the entity it
 * started at, each real tool call in plain words under it (the newest stays in view as the
 * chat follows the end), then the answer streaming in. Every value
 * still comes from Cala; this only shows earlier what the finished answer shows.
 */
export function LiveWalk({ trace }: { trace: WalkTrace }) {
  const profile = useProfile();
  const trusted = new Set((profile.data?.reference_investors ?? []).map((r) => r.entity_id));
  const hidden = Math.max(0, trace.steps.length - VISIBLE_STEPS);
  const steps = trace.steps.slice(hidden);

  return (
    <section className={styles.walk} aria-label="Grabbit walking Cala's graph">
      <header className={styles.head}>
        <span className={styles.title}>Walking Cala's graph</span>
        <span className={styles.budget}>{budgetText(trace)}</span>
      </header>
      {trace.graph && trace.root_id && (
        <ExploredGraphView graph={trace.graph} rootId={trace.root_id} trusted={trusted} live />
      )}
      <ol className={styles.steps} aria-label="Steps" aria-live="polite">
        {hidden > 0 && (
          <li className={styles.earlier}>
            {hidden} earlier step{hidden === 1 ? "" : "s"}
          </li>
        )}
        {steps.map((s) => (
          <Step key={s.id} step={s} />
        ))}
      </ol>
      {trace.answer && (
        <div className={styles.answer}>
          <VisualAnswer ui={trace.answer} graph={trace.graph} streaming={trace.streaming} />
        </div>
      )}
    </section>
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
