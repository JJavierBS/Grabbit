import type { Fact, FactScalar, Source } from "../api/types";
import { humanizeEnum } from "../lib/humanize";
import styles from "./FactValue.module.css";
import { TrustBadge } from "./TrustBadge";

export type FactKind = "auto" | "date";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** The source that sets the fact's trust: the first one with the same rank, else the first. */
export function strongestSource(fact: Fact): Source | undefined {
  return fact.sources.find((s) => s.rank === fact.trust) ?? fact.sources[0];
}

/** A date shows only its precision: a `year` date reads "2019", not "2019-01-01". */
export function formatDate(iso: string, precision: Source["date_precision"] = "day"): string {
  const match = /^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?/.exec(iso);
  if (!match) return iso;
  const [, year, month, day] = match;
  if (precision === "year" || !month) return year;
  const monthName = MONTHS[Number(month) - 1] ?? month;
  if (precision === "month" || !day) return `${monthName} ${year}`;
  return `${Number(day)} ${monthName} ${year}`;
}

/** A number with its unit; currencies read compact from 10,000 on ("€650K"). */
export function formatNumber(value: number, unit?: string | null): string {
  if (unit && /^[A-Z]{3}$/.test(unit)) {
    return new Intl.NumberFormat("en", {
      style: "currency",
      currency: unit,
      notation: Math.abs(value) >= 10_000 ? "compact" : "standard",
      maximumFractionDigits: 1,
    }).format(value);
  }
  const text = new Intl.NumberFormat("en", { maximumFractionDigits: 2 }).format(value);
  return unit ? `${text} ${unit}` : text;
}

function formatScalar(
  value: FactScalar,
  unit: string | null | undefined,
  kind: FactKind,
  fact: Fact,
): string {
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "number") return formatNumber(value, unit);
  if (kind === "date") return formatDate(value, strongestSource(fact)?.date_precision ?? "day");
  const text = humanizeEnum(value);
  return unit ? `${text} ${unit}` : text;
}

/** Text for a fact, or null when Cala has no value (shown as "Not published", never 0). */
export function formatFact(fact: Fact, kind: FactKind = "auto"): string | null {
  const { value, unit } = fact;
  if (value === null || value === undefined || fact.trust === "not_published") return null;
  if (Array.isArray(value)) {
    return value.length ? value.map((v) => formatScalar(v, unit, kind, fact)).join(", ") : null;
  }
  return formatScalar(value, unit, kind, fact);
}

interface FactValueProps {
  fact: Fact;
  label?: string;
  kind?: FactKind;
  /** Inline form for sentences and table cells: value then a compact badge. */
  inline?: boolean;
  /** Spell out the badge's label even inline, where a bare icon would need a tooltip. */
  labelled?: boolean;
}

export function FactValue({
  fact,
  label,
  kind = "auto",
  inline = false,
  labelled = false,
}: FactValueProps) {
  const text = formatFact(fact, kind);
  const source = strongestSource(fact);
  // An absent value is its own badge: "Not published" once, never text plus an empty pill.
  const value =
    text === null ? (
      <TrustBadge level="not_published" />
    ) : (
      <span className={styles.value}>{text}</span>
    );
  const badge =
    text === null ? null : (
      <TrustBadge
        level={fact.trust}
        sourceName={source?.name}
        href={source?.url}
        compact={inline && !labelled}
      />
    );

  if (inline) {
    return (
      <span className={styles.inline}>
        {value}
        {badge}
      </span>
    );
  }
  return (
    <div className={styles.fact}>
      {label && <dt className={styles.label}>{label}</dt>}
      <dd className={styles.body}>
        {value}
        {badge}
      </dd>
    </div>
  );
}
