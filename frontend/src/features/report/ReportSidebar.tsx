import { PanelLeft, RefreshCw } from "lucide-react";
import type { ReactNode } from "react";
import { useReports } from "../../api/hooks/queries";
import type { Report } from "../../api/types";
import { Button } from "../../components/Button";
import { formatDate } from "../../components/FactValue";
import { Skeleton } from "../../components/Skeleton";
import { humanize } from "../../lib/humanize";
import styles from "./ReportSidebar.module.css";
import { KIND_TITLE } from "./ReportView";

/** One report version: a rewrite keeps the id but bumps the profile version. */
export const reportKey = (r: Pick<Report, "id" | "profile_version">) =>
  `${r.id}-${r.profile_version}`;

const time = (iso: string) =>
  new Date(iso).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });

const startups = (n: number) => `${n} ${n === 1 ? "startup" : "startups"}`;

/** An industry inside a sentence: "fintech", but "AI" and "SaaS" keep their capitals. */
function inSentence(word: string): string {
  return /^\p{Lu}[^\p{Lu}]*$/u.test(word.split(" ")[0])
    ? word.replace(/^./, (c) => c.toLowerCase())
    : word;
}

/**
 * A short name for a report in the list: "8 AI startups" when at least half of them share
 * an industry, else "8 startups". The full summary stays in the item's tooltip.
 */
export function shortTitle(report: Pick<Report, "candidates">): string {
  const n = report.candidates.length;
  const counts = new Map<string, number>();
  for (const c of report.candidates) {
    for (const i of new Set(c.industries.map(humanize))) counts.set(i, (counts.get(i) ?? 0) + 1);
  }
  const [top, hits] = [...counts].sort((a, b) => b[1] - a[1])[0] ?? ["", 0];
  if (!n || hits * 2 < n) return startups(n);
  return `${n} ${inSentence(top)} ${n === 1 ? "startup" : "startups"}`;
}

/** "Today", "Yesterday" or the date, like a conversation list. */
export function dayLabel(iso: string, now = new Date()): string {
  const day = (d: Date) => new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
  const diff = Math.round((day(now) - day(new Date(iso))) / 86_400_000);
  if (diff === 0) return "Today";
  if (diff === 1) return "Yesterday";
  return formatDate(iso, "day");
}

interface ReportSidebarProps {
  id: string;
  /** The report version open in the panel, if any. */
  activeKey: string | null;
  onOpen: (report: Report, latest: boolean) => void;
  onClose: () => void;
  /** The logo, or nothing when the top bar already shows it. */
  brand: ReactNode;
  /** Shown above the reports: the research switcher (#145). */
  top?: ReactNode;
  className?: string;
}

/** Every report Grabbit wrote, newest first, grouped by day. */
export function ReportSidebar({
  id,
  activeKey,
  onOpen,
  onClose,
  brand,
  top,
  className,
}: ReportSidebarProps) {
  const reports = useReports();
  const groups: { label: string; items: Report[] }[] = [];
  for (const r of reports.data ?? []) {
    const label = dayLabel(r.created_at);
    const last = groups[groups.length - 1];
    if (last?.label === label) last.items.push(r);
    else groups.push({ label, items: [r] });
  }
  const latestKey = reports.data?.[0] ? reportKey(reports.data[0]) : null;

  return (
    <aside id={id} className={[styles.sidebar, className].filter(Boolean).join(" ")}>
      <div className={styles.head}>
        {brand}
        <Button
          variant="ghost"
          size="sm"
          className={styles.close}
          aria-label="Close sidebar"
          icon={<PanelLeft aria-hidden="true" />}
          onClick={onClose}
        />
      </div>

      <div className={styles.body}>
        {top}
        <nav className={styles.nav} aria-labelledby={`${id}-title`}>
          <h2 id={`${id}-title`} className={styles.heading}>
            Reports
          </h2>

          {reports.isPending && <Skeleton lines={5} label="Loading your reports" />}

          {reports.isError && (
            <div className={styles.error} role="alert">
              <p>Your reports did not load.</p>
              <Button
                variant="secondary"
                size="sm"
                icon={<RefreshCw aria-hidden="true" />}
                onClick={() => reports.refetch()}
              >
                Try again
              </Button>
            </div>
          )}

          {reports.isSuccess && reports.data.length === 0 && (
            <p className={styles.empty}>
              No reports yet. Tell Grabbit what you look for and the first one shows here.
            </p>
          )}

          {groups.map((g) => (
            <section key={g.label} className={styles.group} aria-label={g.label}>
              <h3 className={styles.day}>{g.label}</h3>
              <ul className={styles.list}>
                {g.items.map((r) => {
                  const key = reportKey(r);
                  const latest = key === latestKey;
                  const count = r.candidates.length;
                  return (
                    <li key={key}>
                      <button
                        type="button"
                        className={styles.item}
                        aria-current={key === activeKey ? "true" : undefined}
                        title={r.summary}
                        onClick={() => onOpen(r, latest)}
                      >
                        <span className={styles.summary}>{shortTitle(r)}</span>
                        <span className="visually-hidden">{KIND_TITLE[r.kind]}</span>
                        <span className={styles.meta}>
                          {latest && "Latest · "}
                          {startups(count)} · {time(r.created_at)}
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </section>
          ))}
        </nav>
      </div>
    </aside>
  );
}
