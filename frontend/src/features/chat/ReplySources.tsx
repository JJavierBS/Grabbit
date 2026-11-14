import type { ReplySource } from "../../api/types";
import { TrustBadge } from "../../components/TrustBadge";
import styles from "./ReplySources.module.css";

/** Source names shown in the folded line before "and N more". */
export const SUMMARY_NAMES = 3;

/** Every source once, strongest first (each startup's list already is). */
export function summaryText(cited: ReplySource[]): string {
  const ranked = cited
    .flatMap((c) => c.sources)
    .map((s, i) => ({ s, i }))
    .sort((a, b) => rank(a.s.rank) - rank(b.s.rank) || a.i - b.i)
    .map(({ s }) => s.name);
  const names = [...new Set(ranked)];
  const shown = names.slice(0, SUMMARY_NAMES).join(", ");
  const more = names.length - SUMMARY_NAMES;
  return more > 0 ? `${shown} and ${more} more` : shown;
}

const ORDER = ["filing", "primary", "press", "aggregator", "cala_news", "web_unverified"];
const rank = (level: string) => {
  const i = ORDER.indexOf(level);
  return i === -1 ? ORDER.length : i;
};

/**
 * Where the facts in an agent reply come from (#141): the prose stays clean, and this line
 * names the sources of each startup the reply mentions, with how much to trust each one.
 * The app computes it from Cala's facts; the model never writes it.
 */
export function ReplySources({ cited }: { cited: ReplySource[] }) {
  return (
    <details className={styles.sources}>
      <summary className={styles.summary}>
        <span className={styles.lead}>Sources</span> · {summaryText(cited)}
      </summary>
      <dl className={styles.list}>
        {cited.map((c) => (
          <div key={c.entity_id} className={styles.startup}>
            <dt className={styles.name}>{c.name}</dt>
            <dd className={styles.items}>
              <ul aria-label={`Sources for ${c.name}`}>
                {c.sources.map((s) => (
                  <li key={s.name} className={styles.item}>
                    <TrustBadge level={s.rank} sourceName={s.name} />
                    {s.url ? (
                      <a href={s.url} target="_blank" rel="noopener noreferrer">
                        {s.name}
                      </a>
                    ) : (
                      <span>{s.name}</span>
                    )}
                  </li>
                ))}
              </ul>
            </dd>
          </div>
        ))}
      </dl>
    </details>
  );
}
