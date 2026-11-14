import { useProfile } from "../../api/hooks/queries";
import type { WalkTrace } from "../../api/types";
import styles from "./LiveWalk.module.css";
import { ExploredGraphView } from "./openui/ExploredGraphView";
import { VisualAnswer } from "./openui/VisualAnswer";
import { WalkSteps } from "./WalkSteps";

/** Steps shown at once; older ones fold into a count so the graph stays in view. */
export const VISIBLE_STEPS = 5;

/** What the walk has looked at, in words anyone reads: no "entities", no "nodes". */
export function checkedText(n: number): string {
  if (n === 0) return "nothing checked yet";
  if (n === 1) return "1 company, person or round checked";
  return `${n} companies, people and rounds checked`;
}

export function budgetText(trace: WalkTrace): string {
  const step = trace.round ? `Step ${trace.round} of up to ${trace.max_rounds} · ` : "";
  return `${step}${checkedText(trace.nodes)}`;
}

/**
 * The agent's Cala walk while it happens (#134, #138): the subgraph growing from the entity it
 * started at, each real tool call in plain words under it (the newest stays in view as the
 * chat follows the end), then the answer streaming in. Every value still comes from Cala;
 * this only shows earlier what the finished answer shows.
 */
export function LiveWalk({ trace }: { trace: WalkTrace }) {
  const profile = useProfile();
  const trusted = new Set((profile.data?.reference_investors ?? []).map((r) => r.entity_id));
  const progress = trace.max_rounds ? Math.min(1, trace.round / trace.max_rounds) : 0;

  return (
    <section className={styles.walk} aria-label="Grabbit walking Cala's graph">
      <header className={styles.head}>
        <span className={styles.title}>Reading Cala's map of who funds whom</span>
        <span className={styles.budget}>{budgetText(trace)}</span>
        <span className={styles.bar} aria-hidden="true">
          <span style={{ width: `${progress * 100}%` }} />
        </span>
      </header>
      {trace.graph && trace.root_id && (
        <ExploredGraphView graph={trace.graph} rootId={trace.root_id} trusted={trusted} live />
      )}
      <div aria-live="polite">
        <WalkSteps steps={trace.steps} visible={VISIBLE_STEPS} />
      </div>
      {trace.answer && (
        <div className={styles.answer}>
          <VisualAnswer ui={trace.answer} graph={trace.graph} streaming={trace.streaming} />
        </div>
      )}
    </section>
  );
}
