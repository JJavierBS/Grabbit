import { BellRing, FileSearch, Minus, RefreshCw, Sparkles } from "lucide-react";
import type { ReactNode } from "react";
import { useProfile, useRunReport } from "../../api/hooks/queries";
import type { Candidate, Report } from "../../api/types";
import { Badge } from "../../components/Badge";
import { Button } from "../../components/Button";
import { formatDate } from "../../components/FactValue";
import { Markdown } from "../../components/Markdown";
import { Skeleton } from "../../components/Skeleton";
import { useSettled } from "../../lib/useSettled";
import { CandidateCard } from "./CandidateCard";
import styles from "./ReportView.module.css";
import { type ChangeMark, describeDiff, type ReportDiff } from "./reportDiff";

export const KIND_TITLE: Record<Report["kind"], string> = {
  prep: "Slush 2026 prep report",
  digest: "Digest",
  memo: "Investment memo",
};
const MARK_LABEL: Record<ChangeMark, string> = {
  added: "New",
  moved: "Moved",
  changed: "Rewritten",
};

interface ReportViewProps {
  report: Report | undefined;
  isPending: boolean;
  error: Error | null;
  onRetry: () => void;
  diff: ReportDiff | null;
  /** Confirms the report: the browser asks for notification permission here (flow.md 2). */
  onConfirm?: () => void;
  confirmed?: boolean;
  /** A past report: read only, without the confirm and run actions. */
  archived?: boolean;
}

export function ReportView({
  report,
  isPending,
  error,
  onRetry,
  diff,
  onConfirm,
  confirmed,
  archived,
}: ReportViewProps) {
  const profile = useProfile();
  const run = useRunReport();
  // What changed is tinted for a few seconds, then the tint fades; the badges stay.
  const settled = useSettled(diff);

  if (isPending) {
    return (
      <div className={styles.sheet} aria-busy="true">
        <Skeleton block="title" label="Loading the report" />
        <Skeleton lines={3} />
        <Skeleton block="card" />
        <Skeleton block="card" />
      </div>
    );
  }
  if (!error && !report) {
    return (
      <div className={styles.sheet}>
        <EmptyState title="No report yet">
          Tell Grabbit in the chat what you look for; the first report shows here.
        </EmptyState>
      </div>
    );
  }
  if (error || !report) {
    return (
      <div className={styles.sheet}>
        <div className={styles.state} role="alert">
          <h2 className={styles.stateTitle}>The report did not load</h2>
          <p>{error?.message ?? "Something went wrong."}</p>
          <Button variant="secondary" icon={<RefreshCw aria-hidden="true" />} onClick={onRetry}>
            Try again
          </Button>
        </div>
      </div>
    );
  }

  const trusted = new Set((profile.data?.reference_investors ?? []).map((i) => i.entity_id));
  const byId = new Map(report.candidates.map((c) => [c.entity_id, c]));
  const shown = new Set<string>();
  const lines = diff ? describeDiff(diff) : [];

  return (
    <article className={styles.sheet} aria-labelledby="report-title">
      <header className={styles.header}>
        <div className={styles.meta}>
          <span>{formatDate(report.created_at, "day")}</span>
          <span aria-hidden="true">·</span>
          <span>
            {report.candidates.length} {report.candidates.length === 1 ? "startup" : "startups"}
          </span>
        </div>
        <h2 id="report-title" className={styles.title}>
          {KIND_TITLE[report.kind]}
        </h2>
        <p
          className={styles.summary}
          data-changed={diff?.summaryChanged || undefined}
          data-settled={settled || undefined}
        >
          {report.summary}
        </p>
        {!archived && (
          <div className={styles.actions}>
            {onConfirm && (
              <Button
                icon={<BellRing aria-hidden="true" />}
                onClick={onConfirm}
                disabled={confirmed}
              >
                {confirmed ? "Watching your shortlist" : "Looks right, keep me posted"}
              </Button>
            )}
            <Button
              variant="ghost"
              icon={<RefreshCw aria-hidden="true" />}
              loading={run.isPending}
              onClick={() => run.mutate(report.kind)}
            >
              Run now
            </Button>
          </div>
        )}
        {run.isError && (
          <p className={styles.inlineError} role="alert">
            The report did not run: {run.error.message}
          </p>
        )}
      </header>

      {diff && lines.length > 0 && (
        <div className={styles.banner} role="status">
          <Sparkles aria-hidden="true" className={styles.bannerIcon} />
          <p>
            <strong>Rewritten for you.</strong> {lines.join(" · ")}
          </p>
        </div>
      )}

      {diff?.removedSections.map((title) => (
        <p key={title} className={styles.removed}>
          <Minus aria-hidden="true" />
          <span>Removed section: </span>
          <s>{title}</s>
        </p>
      ))}
      {diff?.removedCandidates.map((c) => (
        <p key={c.entity_id} className={styles.removed}>
          <Minus aria-hidden="true" />
          <span>Removed startup: </span>
          <s>{c.name}</s>
        </p>
      ))}

      {report.sections.length === 0 && report.candidates.length === 0 && (
        <EmptyState title="No startup matches yet">
          Tell Grabbit to widen the thesis in the chat, for example another stage or sector.
        </EmptyState>
      )}

      {report.sections.map((section) => {
        const mark = diff?.sections[section.title];
        const fresh = section.candidate_ids.filter((id) => !shown.has(id) && byId.has(id));
        const seen = section.candidate_ids.filter((id) => shown.has(id) && byId.has(id));
        for (const id of fresh) shown.add(id);
        return (
          <section
            key={section.title}
            className={styles.section}
            data-changed={mark ?? undefined}
            data-settled={(mark && settled) || undefined}
          >
            <div className={styles.sectionHead}>
              <h3 className={styles.sectionTitle}>{section.title}</h3>
              {mark && <Badge tone="warning">{MARK_LABEL[mark]}</Badge>}
            </div>
            <Markdown source={section.body_md} />
            {seen.length > 0 && (
              <SeeAbove candidates={seen.map((id) => byId.get(id) as Candidate)} />
            )}
            {fresh.map((id) => (
              <CandidateCard
                key={id}
                candidate={byId.get(id) as Candidate}
                trusted={trusted}
                mark={diff?.candidates[id]}
                settled={settled}
              />
            ))}
          </section>
        );
      })}

      <Leftovers report={report} shown={shown} trusted={trusted} diff={diff} settled={settled} />
    </article>
  );
}

function SeeAbove({ candidates }: { candidates: Candidate[] }) {
  return (
    <p className={styles.seeAbove}>
      <span>See above: </span>
      {candidates.map((c, i) => (
        <span key={c.entity_id}>
          {i > 0 && ", "}
          <a href={`#candidate-${c.entity_id}`}>{c.name}</a>
        </span>
      ))}
    </p>
  );
}

function Leftovers({
  report,
  shown,
  trusted,
  diff,
  settled,
}: {
  report: Report;
  shown: Set<string>;
  trusted: Set<string>;
  diff: ReportDiff | null;
  settled: boolean;
}) {
  const rest = report.candidates.filter((c) => !shown.has(c.entity_id));
  if (rest.length === 0) return null;
  return (
    <section className={styles.section}>
      <h3 className={styles.sectionTitle}>Other matches</h3>
      {rest.map((c) => (
        <CandidateCard
          key={c.entity_id}
          candidate={c}
          trusted={trusted}
          mark={diff?.candidates[c.entity_id]}
          settled={settled}
        />
      ))}
    </section>
  );
}

/** Nothing to show yet: a calm note with the next step, never styled as an error. */
function EmptyState({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className={styles.empty} data-state="empty">
      <FileSearch aria-hidden="true" className={styles.emptyIcon} />
      <div>
        <h3 className={styles.emptyTitle}>{title}</h3>
        <p>{children}</p>
      </div>
    </div>
  );
}
