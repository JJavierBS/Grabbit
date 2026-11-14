import { FlaskConical, History, RefreshCw, X } from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';
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
import { ReportOutline } from './features/report/ReportOutline';
import { ReportView } from './features/report/ReportView';
import { useReportChanges } from './features/report/useReportChanges';
import styles from './App.module.css';

type Panel = 'report' | 'history';

const PANEL_TITLE: Record<Panel, string> = { report: 'Report', history: 'What changed' };

export const CONFIRM_MESSAGE = 'Looks right, keep me posted.';

const STATUS_TEXT: Record<StreamStatus, string> = {
  connecting: 'Connecting',
  open: 'Live',
  retrying: 'Reconnecting',
};

// Below this width the panel covers the chat instead of sitting beside it.
const NARROW = '(max-width: 63.99rem)';

// The demo trigger shows with the fake API, or with ?demo (fixture name: ?demo=<name>).
const demoParam = new URLSearchParams(location.search).get('demo');
const DEMO_FIXTURE =
  demoParam !== null
    ? demoParam || 'new_round'
    : import.meta.env.VITE_FAKE_API === '1'
      ? 'new_round'
      : null;

export function App() {
  const [panel, setPanel] = useState<Panel | null>(null);
  const [confirmed, setConfirmed] = useState(false);
  const report = useLatestReport();
  const diff = useReportChanges(report.data);
  const send = useSendMessage();
  const simulate = useSimulateEvent();
  const [openAlert, setOpenAlert] = useState<Alert | null>(null);
  const panelRef = useRef<HTMLElement>(null);
  const returnFocus = useRef<HTMLElement | null>(null);

  const openPanel = useCallback((next: Panel) => {
    if (document.activeElement instanceof HTMLElement) returnFocus.current = document.activeElement;
    setPanel(next);
  }, []);

  const closePanel = useCallback(() => {
    setPanel(null);
    returnFocus.current?.focus();
  }, []);

  const showAlert = useCallback((alert: Alert) => {
    setOpenAlert(alert);
    // The alert opens in the chat; on narrow screens the panel would hide it.
    if (window.matchMedia?.(NARROW).matches) setPanel(null);
  }, []);
  const deliver = useAlertDelivery(showAlert);
  const stream = useEvents(deliver);

  // A rewrite is the moment to watch: open the report on the change.
  useEffect(() => {
    if (diff) setPanel('report');
  }, [diff]);

  useEffect(() => {
    if (!panel) return;
    panelRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closePanel();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [panel, closePanel]);

  const confirm = () => {
    setConfirmed(true);
    void askNotificationPermission();
    send.mutate(CONFIRM_MESSAGE);
  };

  const reportInChat = report.data ? (
    <ReportOutline
      key={report.data.id}
      report={report.data}
      open={panel === 'report'}
      rewritten={diff !== null}
      onOpen={() => openPanel('report')}
    />
  ) : report.isError ? (
    <div className={styles.reportError} role="alert">
      <p className={styles.reportErrorTitle}>The report did not load</p>
      <p>{report.error.message}</p>
      <Button
        variant="secondary"
        size="sm"
        icon={<RefreshCw aria-hidden="true" />}
        onClick={() => report.refetch()}
      >
        Try again
      </Button>
    </div>
  ) : null;

  return (
    <div className={styles.app}>
      <header className={styles.topbar}>
        <div className={styles.brand}>
          <svg className={styles.mark} viewBox="0 0 144 84" aria-hidden="true">
            <rect x="38" y="2" width="104" height="28" rx="14" />
            <rect x="2" y="52" width="128" height="29" rx="14.5" />
          </svg>
          <h1 className={styles.wordmark}>Grabbit</h1>
        </div>
        <span className={styles.status} data-status={stream} role="status">
          {STATUS_TEXT[stream]}
        </span>
        <div className={styles.actions}>
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
          <Button
            variant="ghost"
            size="sm"
            icon={<History aria-hidden="true" />}
            aria-pressed={panel === 'history'}
            onClick={() => (panel === 'history' ? closePanel() : openPanel('history'))}
          >
            What changed
          </Button>
          {import.meta.env.VITE_FAKE_API === '1' && <Badge tone="warning">Demo data</Badge>}
        </div>
      </header>

      <main className={styles.main} data-panel={panel ?? undefined}>
        <div className={styles.chat}>
          <ChatPanel
            footer={
              <>
                {reportInChat}
                {openAlert && <AlertCard alert={openAlert} onClose={() => setOpenAlert(null)} />}
              </>
            }
          />
        </div>
        {panel && (
          <section
            ref={panelRef}
            id="report-panel"
            className={styles.panel}
            aria-labelledby="panel-title"
            // biome-ignore lint/a11y/noNoninteractiveTabindex: a scrollable region needs keyboard focus (axe scrollable-region-focusable).
            tabIndex={0}
          >
            <div className={styles.panelBar}>
              <h2 id="panel-title" className={styles.panelTitle}>
                {PANEL_TITLE[panel]}
              </h2>
              <Button
                variant="ghost"
                size="sm"
                aria-label="Close panel"
                icon={<X aria-hidden="true" />}
                onClick={closePanel}
              />
            </div>
            {panel === 'history' ? (
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
          </section>
        )}
      </main>
    </div>
  );
}
