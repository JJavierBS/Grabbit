import { ArrowRight, RefreshCw } from "lucide-react";
import { useProfile, useProfileHistory } from "../../api/hooks/queries";
import type { ProfileChange } from "../../api/types";
import { Badge } from "../../components/Badge";
import { Button } from "../../components/Button";
import { Skeleton } from "../../components/Skeleton";
import { humanizeEnum } from "../../lib/humanize";
import styles from "./ProfileHistory.module.css";

const FIELD_LABELS: Record<string, string> = {
  instructions: "Its own report instructions",
  thesis: "Thesis",
  reference_investors: "Reference investors",
  sources: "News sources",
  "filters.stages": "Stages",
  "filters.sectors_in": "Sectors to include",
  "filters.sectors_out": "Sectors to leave out",
  "filters.countries": "Countries",
  "filters.headcount_max": "Largest team size",
  "filters.ticket": "Ticket",
  "style.length": "Report length",
  "style.detail": "Level of detail",
  "style.sections": "Section order",
  cadence: "Cadence",
  alert_threshold: "Alert threshold",
};

export const fieldLabel = (field: string) =>
  FIELD_LABELS[field] ??
  field
    .replace(/^[a-z]+\./, "")
    .replace(/_/g, " ")
    .replace(/^./, (c) => c.toUpperCase());

/** A before/after value as plain text; empty values read "nothing". */
export function formatChangeValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "nothing";
  if (Array.isArray(value)) {
    return value.length ? value.map(formatChangeValue).join(", ") : "nothing";
  }
  if (typeof value === "object") {
    if ("name" in value) return String((value as { name: unknown }).name);
    if ("value" in value) return formatChangeValue((value as { value: unknown }).value);
    return JSON.stringify(value);
  }
  return humanizeEnum(String(value));
}

export function ProfileHistory() {
  const history = useProfileHistory();
  const profile = useProfile();

  return (
    <article className={styles.sheet} aria-labelledby="history-title">
      <header className={styles.header}>
        <h2 id="history-title" className={styles.title}>
          What Grabbit changed about itself
        </h2>
        <p className={styles.lead}>
          Every correction edits your profile and, when needed, the instructions Grabbit writes for
          itself. Each line says why.
        </p>
      </header>

      {profile.data && (
        <section className={styles.current} aria-label="Current instructions">
          <h3 className={styles.currentTitle}>How it writes for you now</h3>
          <blockquote className={styles.quote}>
            {profile.data.instructions || "No instructions yet."}
          </blockquote>
          <p className={styles.meta}>Profile version {profile.data.version}</p>
        </section>
      )}

      {history.isPending && <Skeleton lines={6} label="Loading the history" />}
      {history.isError && (
        <div className={styles.error} role="alert">
          <p>{history.error.message}</p>
          <Button
            variant="secondary"
            size="sm"
            icon={<RefreshCw aria-hidden="true" />}
            onClick={() => history.refetch()}
          >
            Try again
          </Button>
        </div>
      )}
      {history.isSuccess && history.data.length === 0 && (
        <p className={styles.empty}>
          No changes yet. Correct the report in the chat and the change appears here.
        </p>
      )}
      {history.isSuccess && history.data.length > 0 && (
        <ol className={styles.list}>
          {history.data.map((change) => (
            <ChangeRow key={`${change.version}-${change.field}`} change={change} />
          ))}
        </ol>
      )}
    </article>
  );
}

function ChangeRow({ change }: { change: ProfileChange }) {
  return (
    <li className={styles.row}>
      <div className={styles.rowHead}>
        <span className={styles.version}>v{change.version}</span>
        <span className={styles.field}>{fieldLabel(change.field)}</span>
        <Badge tone={change.by === "agent" ? "ink" : "neutral"}>
          {change.by === "agent" ? "By Grabbit" : "By you"}
        </Badge>
      </div>
      <p className={styles.diff}>
        <span className={styles.before}>{formatChangeValue(change.before)}</span>
        <ArrowRight aria-label="became" className={styles.arrow} />
        <span className={styles.after}>{formatChangeValue(change.after)}</span>
      </p>
      <p className={styles.reason}>{change.reason}</p>
    </li>
  );
}
