import { useId, useState } from "react";
import type { NewsItem } from "../../api/types";
import { formatFact, strongestSource } from "../../components/FactValue";
import { TrustBadge } from "../../components/TrustBadge";
import styles from "./CalaNews.module.css";

/** Longer summaries start folded to one line; shorter ones always fit. */
const FOLD_AT = 90;

interface CalaNewsProps {
  items: NewsItem[];
  /** Startup name, for the accessible names. */
  name: string;
  /** The heading level of the block; the card uses h5, a chat answer h6. */
  heading?: "h5" | "h6";
}

/**
 * Latest news about a startup from Cala's knowledge query. Each item says only what Cala
 * says: a title, a date at its precision and a summary, with no per-item source link, so
 * the block carries the "Cala news" badge and stays apart from web signals.
 */
export function CalaNews({ items, name, heading: Heading = "h5" }: CalaNewsProps) {
  if (items.length === 0) return null;
  return (
    <section className={styles.news} aria-label={`News about ${name} from Cala`}>
      <div className={styles.head}>
        <Heading className={styles.title}>Latest news</Heading>
        <TrustBadge level="cala_news" sourceName="Cala knowledge query, no per-item source" />
      </div>
      <ol className={styles.list}>
        {items.map((item) => (
          <NewsRow key={`${item.title}-${item.date.value ?? ""}`} item={item} />
        ))}
      </ol>
    </section>
  );
}

function NewsRow({ item }: { item: NewsItem }) {
  const [open, setOpen] = useState(false);
  const summaryId = useId();
  const date = formatFact(item.date, "date");
  const iso = strongestSource(item.date)?.date ?? undefined;
  const folds = (item.summary?.length ?? 0) > FOLD_AT;
  return (
    <li className={styles.item}>
      {date ? (
        <time className={styles.date} dateTime={iso}>
          {date}
        </time>
      ) : (
        <span className={styles.dateAbsent}>Date not published</span>
      )}
      <p className={styles.headline}>{item.title}</p>
      {item.summary && (
        <div className={styles.summaryRow}>
          <p id={summaryId} className={styles.summary} data-open={!folds || open}>
            {item.summary}
          </p>
          {folds && (
            <button
              type="button"
              className={styles.more}
              aria-expanded={open}
              aria-controls={summaryId}
              onClick={() => setOpen((v) => !v)}
            >
              {open ? "Less" : "More"}
            </button>
          )}
        </div>
      )}
      {item.entities.length > 0 && (
        <ul className={styles.entities} aria-label="Mentioned in Cala">
          {item.entities.map((e) => (
            <li
              key={e.entity_id}
              className={styles.entity}
              data-entity-id={e.entity_id}
              title={`${e.entity_type} in Cala, id ${e.entity_id}`}
            >
              {e.name}
              <span className={styles.entityType}>{e.entity_type}</span>
            </li>
          ))}
        </ul>
      )}
    </li>
  );
}
