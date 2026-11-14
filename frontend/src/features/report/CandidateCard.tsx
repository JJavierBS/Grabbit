import { ExternalLink } from "lucide-react";
import type { Candidate, Round, Signal } from "../../api/types";
import { Badge } from "../../components/Badge";
import { FactValue } from "../../components/FactValue";
import { CalaNews } from "./CalaNews";
import { CalaPath } from "./CalaPath";
import styles from "./CandidateCard.module.css";
import type { ChangeMark } from "./reportDiff";

const MARK_LABEL: Record<ChangeMark, string> = {
  added: "New",
  moved: "Moved",
  changed: "Rewritten",
};

interface CandidateCardProps {
  candidate: Candidate;
  trusted: Set<string>;
  mark?: ChangeMark;
}

export function CandidateCard({ candidate, trusted, mark }: CandidateCardProps) {
  const c = candidate;
  return (
    <article
      id={`candidate-${c.entity_id}`}
      className={styles.card}
      data-changed={mark ?? undefined}
    >
      <header className={styles.header}>
        <div className={styles.titleRow}>
          <h4 className={styles.name}>{c.name}</h4>
          {mark && <Badge tone="warning">{MARK_LABEL[mark]}</Badge>}
          {c.website && (
            <a className={styles.site} href={c.website} target="_blank" rel="noopener noreferrer">
              Website
              <ExternalLink aria-hidden="true" />
            </a>
          )}
        </div>
        {c.description && <p className={styles.description}>{c.description}</p>}
        {c.industries.length > 0 && (
          <ul className={styles.tags} aria-label="Industries">
            {c.industries.map((i) => (
              <li key={i}>
                <Badge>{i}</Badge>
              </li>
            ))}
          </ul>
        )}
      </header>

      <dl className={styles.facts}>
        <FactValue label="Founded" kind="date" fact={c.founding_date} />
        <FactValue label="Stage" fact={c.funding_stage} />
        <FactValue label="Team" fact={c.headcount} />
        <FactValue label="Total raised" fact={c.total_funding} />
        <FactValue label="Headquarters" fact={c.hq} />
      </dl>

      {c.rounds.length > 0 && (
        <section className={styles.block} aria-label={`Why ${c.name} is here`}>
          <h5 className={styles.blockTitle}>Why it is here</h5>
          <CalaPath candidate={c} trusted={trusted} />
        </section>
      )}

      {c.signals.length > 0 && (
        <section className={styles.block} aria-label={`Signals for ${c.name}`}>
          <h5 className={styles.blockTitle}>Signals</h5>
          <ul className={styles.signals}>
            {c.signals.map((s) => (
              <SignalRow key={s.kind} signal={s} />
            ))}
          </ul>
        </section>
      )}

      <CalaNews items={c.news} name={c.name} />

      <section className={styles.block} aria-label={`Rounds of ${c.name}`}>
        <h5 className={styles.blockTitle}>Rounds</h5>
        {c.rounds.length === 0 ? (
          <p className={styles.muted}>No funding round in Cala.</p>
        ) : (
          <ul className={styles.rounds}>
            {c.rounds.map((r) => (
              <RoundRow key={r.entity_id} round={r} trusted={trusted} />
            ))}
          </ul>
        )}
      </section>
    </article>
  );
}

function RoundRow({ round, trusted }: { round: Round; trusted: Set<string> }) {
  const lead = round.investors.filter((i) => i.is_lead);
  const others = round.investors.filter((i) => !i.is_lead);
  return (
    <li className={styles.round}>
      <div className={styles.roundHead}>
        <span className={styles.roundLabel}>{round.label ?? round.name}</span>
        <FactValue inline kind="date" fact={round.date} />
        <FactValue inline fact={round.amount} />
      </div>
      <p className={styles.investors}>
        {lead.length > 0 && (
          <>
            <span className={styles.muted}>Led by </span>
            {lead.map((i, n) => (
              <span key={i.entity_id}>
                {n > 0 && ", "}
                <InvestorName name={i.name} trusted={trusted.has(i.entity_id)} />
              </span>
            ))}
          </>
        )}
        {lead.length === 0 && <span className={styles.muted}>Lead not published</span>}
        {others.length > 0 && (
          <>
            <span className={styles.muted}> · with </span>
            {others.map((i, n) => (
              <span key={i.entity_id}>
                {n > 0 && ", "}
                <InvestorName name={i.name} trusted={trusted.has(i.entity_id)} />
              </span>
            ))}
          </>
        )}
      </p>
    </li>
  );
}

function InvestorName({ name, trusted }: { name: string; trusted: boolean }) {
  return (
    <span className={styles.investor}>
      {name}
      {trusted && <Badge tone="ink">You trust</Badge>}
    </span>
  );
}

function signalStatus(s: Signal): { text: string; tone: "info" | "neutral" } {
  if (s.value === null || s.value === undefined)
    return { text: "Not enough data", tone: "neutral" };
  if (s.value === false) return { text: "Not now", tone: "neutral" };
  if (typeof s.value === "number") return { text: `${Math.round(s.value * 100)}%`, tone: "info" };
  if (Array.isArray(s.value))
    return { text: `${s.value.length} match${s.value.length === 1 ? "" : "es"}`, tone: "info" };
  return { text: "Yes", tone: "info" };
}

function SignalRow({ signal }: { signal: Signal }) {
  const status = signalStatus(signal);
  return (
    <li className={styles.signal}>
      <div className={styles.signalHead}>
        <span className={styles.signalLabel}>{signal.label}</span>
        <Badge tone={status.tone}>{status.text}</Badge>
      </div>
      <p className={styles.explanation}>{signal.explanation}</p>
      {signal.facts.length > 0 && (
        <p className={styles.signalFacts}>
          {signal.facts.map((f, i) => (
            // biome-ignore lint/suspicious/noArrayIndexKey: facts have no id and never reorder here.
            <FactValue key={i} inline fact={f} />
          ))}
        </p>
      )}
    </li>
  );
}
