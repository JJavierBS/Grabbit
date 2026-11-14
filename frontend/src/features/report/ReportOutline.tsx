import { FileText } from "lucide-react";
import type { Report } from "../../api/types";
import { Badge } from "../../components/Badge";
import { formatDate } from "../../components/FactValue";
import { WorkingLine } from "../chat/WorkingLine";
import styles from "./ReportOutline.module.css";
import { KIND_TITLE } from "./ReportView";
import { REWRITING_TEXT } from "./useReportRewriting";

interface ReportOutlineProps {
  report: Report;
  open: boolean;
  rewritten: boolean;
  /** A newer profile's report is being written: this one is about to be replaced. */
  rewriting?: boolean;
  onOpen: () => void;
}

/** The report as it shows in the chat: title, sections and size. The full report opens in the side panel. */
export function ReportOutline({ report, open, rewritten, rewriting, onOpen }: ReportOutlineProps) {
  const title = KIND_TITLE[report.kind];
  const count = report.candidates.length;
  return (
    <article
      className={styles.card}
      aria-label={`${title} outline`}
      aria-busy={rewriting || undefined}
      data-rewriting={rewriting || undefined}
    >
      {rewriting && <WorkingLine hasReport phase={REWRITING_TEXT} />}
      <div className={styles.head}>
        <h3 className={styles.title}>{title}</h3>
        {rewritten && <Badge tone="warning">Rewritten</Badge>}
      </div>
      <p className={styles.meta}>
        {formatDate(report.created_at, "day")} · {count} {count === 1 ? "startup" : "startups"}
      </p>
      {report.sections.length > 0 && (
        <ol className={styles.sections}>
          {report.sections.map((s) => (
            <li key={s.title}>{s.title}</li>
          ))}
        </ol>
      )}
      <button
        type="button"
        className={styles.open}
        aria-expanded={open}
        aria-controls="report-panel"
        onClick={onOpen}
      >
        <FileText aria-hidden="true" />
        {open ? "Report is open" : "Open report"}
      </button>
    </article>
  );
}
