import { FlaskConical } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import { useLatestReport, useSendMessage, useSimulateEvent } from './api/hooks/queries';
import { type StreamStatus, useEvents } from './api/hooks/useEvents';
import type { Alert } from './api/types';
import { Badge } from './components/Badge';
import { Button } from './components/Button';
import { AlertCard } from './features/alerts/AlertCard';
import { askNotificationPermission } from './features/alerts/notify';
import { useAlertDelivery } from './features/alerts/useAlertDelivery';
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

const STATUS_TEXT: Record<StreamStatus, string> = {
  connecting: 'Connecting',
  open: 'Live',
  retrying: 'Reconnecting',
};

// The demo trigger shows with the fake API, or with ?demo (fixture name: ?demo=<name>).
const demoParam = new URLSearchParams(location.search).get('demo');
const DEMO_FIXTURE =
  demoParam !== null
    ? demoParam || 'new_round'
    : import.meta.env.VITE_FAKE_API === '1'
      ? 'new_round'
      : null;

export function App() {
  const [view, setView] = useState<View>('report');
  const [confirmed, setConfirmed] = useState(false);
  const report = useLatestReport();
  const diff = useReportChanges(report.data);
  const send = useSendMessage();
  const simulate = useSimulateEvent();
  const [openAlert, setOpenAlert] = useState<Alert | null>(null);

  const showAlert = useCallback((alert: Alert) => {
    setOpenAlert(alert);
    // The chat is always visible on wide screens; only narrow ones must switch to it.
    if (window.matchMedia?.('(max-width: 63.99rem)').matches) setView('chat');
  }, []);
  const deliver = useAlertDelivery(showAlert);
  const stream = useEvents(deliver);

  // A rewrite is the moment to watch: bring the report into view wherever the user is.
  useEffect(() => {
    if (diff) setView('report');
  }, [diff]);

  const confirm = () => {
    setConfirmed(true);
    void askNotificationPermission();
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
        <span className={styles.status} data-status={stream} role="status">
          {STATUS_TEXT[stream]}
        </span>
        {DEMO_FIXTURE && (
          <Button
            variant="ghost"
            size="sm"
            icon={<FlaskConical aria-hidden="true" />}
            loading={simulate.isPending}
            onClick={() => simulate.mutate(DEMO_FIXTURE)}
          >
            Simulate event
          </Button>
        )}
        {import.meta.env.VITE_FAKE_API === '1' && (
          <Badge tone="warning" className={styles.demo}>
            Demo data
          </Badge>
        )}
      </header>

      <main className={styles.main} data-view={view}>
        <div className={styles.chat}>
          <ChatPanel
            footer={
              openAlert ? <AlertCard alert={openAlert} onClose={() => setOpenAlert(null)} /> : null
            }
          />
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
