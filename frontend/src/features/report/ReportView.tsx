import { BellRing, Minus, RefreshCw, Sparkles } from 'lucide-react';
import { useProfile, useRunReport } from '../../api/hooks/queries';
import type { Candidate, Report } from '../../api/types';
import { Badge } from '../../components/Badge';
import { Button } from '../../components/Button';
import { Markdown } from '../../components/Markdown';
import { Skeleton } from '../../components/Skeleton';
import { formatDate } from '../../components/FactValue';
import { CandidateCard } from './CandidateCard';
import { type ChangeMark, describeDiff, type ReportDiff } from './reportDiff';
import styles from './ReportView.module.css';

export const KIND_TITLE: Record<Report['kind'], string> = {
  prep: 'Slush 2026 prep report',
  digest: 'Digest',
  memo: 'Investment memo',
};
const MARK_LABEL: Record<ChangeMark, string> = {
  added: 'New',
  moved: 'Moved',
  changed: 'Rewritten',
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
  if (error || !report) {
    return (
      <div className={styles.sheet}>
        <div className={styles.state} role="alert">
          <h2 className={styles.stateTitle}>The report did not load</h2>
          <p>{error?.message ?? 'There is no report yet.'}</p>
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
          <span>{formatDate(report.created_at, 'day')}</span>
          <span aria-hidden="true">·</span>
          <span>Profile version {report.profile_version}</span>
        </div>
        <h2 id="report-title" className={styles.title}>
          {KIND_TITLE[report.kind]}
        </h2>
        <p className={styles.summary} data-changed={diff?.summaryChanged || undefined}>
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
                {confirmed ? 'Watching your shortlist' : 'Looks right, keep me posted'}
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
            <strong>Rewritten for you.</strong> {lines.join(' · ')}
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
        <div className={styles.state}>
          <h3 className={styles.stateTitle}>No startup matches yet</h3>
          <p>Tell Grabbit to widen the thesis in the chat, for example another stage or sector.</p>
        </div>
      )}

      {report.sections.map((section) => {
        const mark = diff?.sections[section.title];
        const fresh = section.candidate_ids.filter((id) => !shown.has(id) && byId.has(id));
        const seen = section.candidate_ids.filter((id) => shown.has(id) && byId.has(id));
        for (const id of fresh) shown.add(id);
        return (
          <section key={section.title} className={styles.section} data-changed={mark ?? undefined}>
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
              />
            ))}
          </section>
        );
      })}

      <Leftovers report={report} shown={shown} trusted={trusted} diff={diff} />
    </article>
  );
}

function SeeAbove({ candidates }: { candidates: Candidate[] }) {
  return (
    <p className={styles.seeAbove}>
      <span>See above: </span>
      {candidates.map((c, i) => (
        <span key={c.entity_id}>
          {i > 0 && ', '}
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
}: {
  report: Report;
  shown: Set<string>;
  trusted: Set<string>;
  diff: ReportDiff | null;
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
        />
      ))}
    </section>
  );
}
