import { ChevronRight, RefreshCw } from 'lucide-react';
import { useReports } from '../../api/hooks/queries';
import type { Report } from '../../api/types';
import { Badge } from '../../components/Badge';
import { Button } from '../../components/Button';
import { formatDate } from '../../components/FactValue';
import { Skeleton } from '../../components/Skeleton';
import styles from './ReportList.module.css';
import { KIND_TITLE } from './ReportView';

const time = (iso: string) =>
  new Date(iso).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });

/** Every report Grabbit wrote, newest first. Opening one shows it in the panel. */
export function ReportList({ onOpen }: { onOpen: (report: Report) => void }) {
  const reports = useReports();

  if (reports.isPending) return <Skeleton lines={4} label="Loading your reports" />;
  if (reports.isError) {
    return (
      <div className={styles.state} role="alert">
        <p className={styles.stateTitle}>Your reports did not load</p>
        <p>{reports.error.message}</p>
        <Button
          variant="secondary"
          size="sm"
          icon={<RefreshCw aria-hidden="true" />}
          onClick={() => reports.refetch()}
        >
          Try again
        </Button>
      </div>
    );
  }
  if (reports.data.length === 0) {
    return (
      <p className={styles.empty}>
        No reports yet. Tell Grabbit what you look for and it writes the first one.
      </p>
    );
  }

  return (
    <ul className={styles.list}>
      {reports.data.map((r, i) => (
        <li key={`${r.id}-${r.profile_version}`}>
          <button type="button" className={styles.item} onClick={() => onOpen(r)}>
            <span className={styles.main}>
              <span className={styles.title}>
                {KIND_TITLE[r.kind]}
                {i === 0 && <Badge tone="neutral">Latest</Badge>}
              </span>
              <span className={styles.meta}>
                {formatDate(r.created_at, 'day')}, {time(r.created_at)} · {r.candidates.length}{' '}
                {r.candidates.length === 1 ? 'startup' : 'startups'} · Profile version{' '}
                {r.profile_version}
              </span>
            </span>
            <ChevronRight aria-hidden="true" className={styles.chevron} />
          </button>
        </li>
      ))}
    </ul>
  );
}
