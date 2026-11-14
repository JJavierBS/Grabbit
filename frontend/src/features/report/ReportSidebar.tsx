import { PanelLeftClose, RefreshCw } from "lucide-react";
import type { ReactNode } from "react";
import { useReports } from "../../api/hooks/queries";
import type { Report } from "../../api/types";
import { Button } from "../../components/Button";
import { formatDate } from "../../components/FactValue";
import { Skeleton } from "../../components/Skeleton";
import styles from "./ReportSidebar.module.css";
import { KIND_TITLE } from "./ReportView";

/** One report version: a rewrite keeps the id but bumps the profile version. */
export const reportKey = (r: Pick<Report, "id" | "profile_version">) =>
  `${r.id}-${r.profile_version}`;

const time = (iso: string) =>
  new Date(iso).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });

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
  className?: string;
}

/** Every report Grabbit wrote, newest first, grouped by day. */
export function ReportSidebar({
  id,
  activeKey,
  onOpen,
  onClose,
  brand,
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
          icon={<PanelLeftClose aria-hidden="true" />}
          onClick={onClose}
        />
      </div>

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
                      onClick={() => onOpen(r, latest)}
                    >
                      <span className={styles.summary}>{r.summary}</span>
                      <span className="visually-hidden">{KIND_TITLE[r.kind]}</span>
                      <span className={styles.meta}>
                        {latest && "Latest · "}
                        {time(r.created_at)} · {count} {count === 1 ? "startup" : "startups"} · v
                        {r.profile_version}
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </section>
        ))}
      </nav>
    </aside>
  );
}
