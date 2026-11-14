import { useEffect, useState } from 'react';
import { useLatestReport, useSendMessage } from './api/hooks/queries';
import { Badge } from './components/Badge';
import { ChatPanel } from './features/chat/ChatPanel';
import { ProfileHistory } from './features/profile/ProfileHistory';
import { ReportView } from './features/report/ReportView';
import { useReportChanges } from './features/report/useReportChanges';
import styles from './App.module.css';

type View = 'chat' | 'report' | 'history';

const VIEWS: { id: View; label: string }[] = [
  { id: 'chat', label: 'Chat' },
  { id: 'report', label: 'Report' },
  { id: 'history', label: 'What changed' },
];

export const CONFIRM_MESSAGE = 'Looks right, keep me posted.';

export function App() {
  const [view, setView] = useState<View>('report');
  const [confirmed, setConfirmed] = useState(false);
  const report = useLatestReport();
  const diff = useReportChanges(report.data);
  const send = useSendMessage();

  // A rewrite is the moment to watch: bring the report into view wherever the user is.
  useEffect(() => {
    if (diff) setView('report');
  }, [diff]);

  const confirm = () => {
    setConfirmed(true);
    send.mutate(CONFIRM_MESSAGE);
  };

  return (
    <div className={styles.app}>
      <header className={styles.topbar}>
        <div className={styles.brand}>
          <span className={styles.wordmark}>Grabbit</span>
          <span className={styles.tagline}>Your research agent for Slush 2026</span>
        </div>
        <nav className={styles.switch} aria-label="Views">
          {VIEWS.map((v) => (
            <button
              key={v.id}
              type="button"
              className={styles.switchItem}
              data-view={v.id}
              aria-pressed={view === v.id}
              onClick={() => setView(v.id)}
            >
              {v.label}
            </button>
          ))}
        </nav>
        {import.meta.env.VITE_FAKE_API === '1' && (
          <Badge tone="warning" className={styles.demo}>
            Demo data
          </Badge>
        )}
      </header>

      <main className={styles.main} data-view={view}>
        <div className={styles.chat}>
          <ChatPanel />
        </div>
        <div className={styles.stage}>
          {view === 'history' ? (
            <ProfileHistory />
          ) : (
            <ReportView
              report={report.data}
              isPending={report.isPending}
              error={report.error}
              onRetry={() => report.refetch()}
              diff={diff}
              onConfirm={confirm}
              confirmed={confirmed}
            />
          )}
        </div>
      </main>
    </div>
  );
}
