import { BellRing, X } from "lucide-react";
import type { Alert } from "../../api/types";
import { Badge } from "../../components/Badge";
import { FactValue, formatDate } from "../../components/FactValue";
import styles from "./AlertCard.module.css";
import { SimulatedBadge } from "./useAlertDelivery";

const KIND_LABEL: Record<Alert["kind"], string> = {
  new_round: "New round",
  executive_change: "Executive change",
  headcount_jump: "Headcount jump",
  acquisition: "Acquisition",
  status_change: "Status change",
  web_news: "Web news",
};

/** An alert opened in the chat, with why it matters and its facts with trust badges. */
export function AlertCard({ alert, onClose }: { alert: Alert; onClose?: () => void }) {
  return (
    <article className={styles.card} aria-labelledby={`alert-${alert.id}`} tabIndex={-1}>
      <div className={styles.head}>
        <BellRing className={styles.icon} aria-hidden="true" />
        <Badge tone="ink">{KIND_LABEL[alert.kind]}</Badge>
        {alert.simulated && <SimulatedBadge />}
        <span className={styles.time}>{formatDate(alert.created_at, "day")}</span>
        {onClose && (
          <button type="button" className={styles.close} aria-label="Close alert" onClick={onClose}>
            <X aria-hidden="true" />
          </button>
        )}
      </div>
      <h3 id={`alert-${alert.id}`} className={styles.title}>
        {alert.title}
      </h3>
      <p className={styles.entity}>{alert.entity_name}</p>
      <div className={styles.why}>
        <span className={styles.whyLabel}>Why it matters</span>
        <p>{alert.why_it_matters}</p>
      </div>
      {alert.facts.length > 0 && (
        <ul className={styles.facts} aria-label="Facts behind this alert">
          {alert.facts.map((f, i) => (
            // biome-ignore lint/suspicious/noArrayIndexKey: alert facts have no id and never reorder.
            <li key={i}>
              <FactValue inline labelled fact={f} />
            </li>
          ))}
        </ul>
      )}
    </article>
  );
}
