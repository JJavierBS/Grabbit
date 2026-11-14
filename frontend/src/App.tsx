import { ArrowLeft, Bell, FileText, History, RefreshCw, X } from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useLatestReport, useSendMessage, useSimulateEvent } from './api/hooks/queries';
import { type StreamStatus, useEvents } from './api/hooks/useEvents';
import type { Alert, Report } from './api/types';
import { Button } from './components/Button';
import { AlertCard } from './features/alerts/AlertCard';
import { askNotificationPermission } from './features/alerts/notify';
import { useAlertDelivery } from './features/alerts/useAlertDelivery';
import { ChatPanel } from './features/chat/ChatPanel';
import { ProfileHistory } from './features/profile/ProfileHistory';
import { ReportList } from './features/report/ReportList';
import { ReportOutline } from './features/report/ReportOutline';
import { ReportView } from './features/report/ReportView';
import { useReportChanges } from './features/report/useReportChanges';
import styles from './App.module.css';

type Panel = 'report' | 'reports' | 'history';

const PANEL_TITLE: Record<Panel, string> = {
  report: 'Report',
  reports: 'Reports',
  history: 'What changed',
};

/** The demo alert arrives this long after the click, so it lands like a real one. */
export const ALERT_DELAY_MS = 30_000;

export const CONFIRM_MESSAGE = 'Looks right, keep me posted.';

const STATUS_TEXT: Record<StreamStatus, string> = {
  connecting: 'Connecting',
  open: 'Live',
  retrying: 'Reconnecting',
};

// Below this width the panel covers the chat instead of sitting beside it.
const NARROW = '(max-width: 63.99rem)';

// The demo trigger shows with the fake API, or with ?demo (fixture name: ?demo=<name>).
function demoFixture(): string | null {
  const param = new URLSearchParams(location.search).get('demo');
  if (param !== null) return param || 'new_round';
  return import.meta.env.VITE_FAKE_API === '1' ? 'new_round' : null;
}

export function App() {
  const [panel, setPanel] = useState<Panel | null>(null);
  const [demo] = useState(demoFixture);
  const [confirmed, setConfirmed] = useState(false);
  const report = useLatestReport();
  const diff = useReportChanges(report.data);
  const send = useSendMessage();
  const simulate = useSimulateEvent();
  const [openAlert, setOpenAlert] = useState<Alert | null>(null);
  // A past report opened from the Reports list; null shows the latest one.
  const [pastReport, setPastReport] = useState<Report | null>(null);
  const [alertQueued, setAlertQueued] = useState(false);
  const alertTimer = useRef<number | undefined>(undefined);
  const panelRef = useRef<HTMLElement>(null);
  const returnFocus = useRef<HTMLElement | null>(null);

  const openPanel = useCallback((next: Panel) => {
    if (document.activeElement instanceof HTMLElement) returnFocus.current = document.activeElement;
    setPastReport(null);
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
    if (!diff) return;
    setPastReport(null);
    setPanel('report');
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

  useEffect(() => () => window.clearTimeout(alertTimer.current), []);

  const queueAlert = (fixture: string) => {
    setAlertQueued(true);
    alertTimer.current = window.setTimeout(() => {
      simulate.mutate(fixture, { onSettled: () => setAlertQueued(false) });
    }, ALERT_DELAY_MS);
  };

  const confirm = () => {
    setConfirmed(true);
    void askNotificationPermission();
    send.mutate(CONFIRM_MESSAGE);
  };

  const reportInChat = report.data ? (
    <ReportOutline
      key={report.data.id}
      report={report.data}
      open={panel === 'report' && pastReport === null}
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
          {demo && (
            <Button
              variant="ghost"
              size="sm"
              icon={<Bell aria-hidden="true" />}
              disabled={alertQueued}
              onClick={() => queueAlert(demo)}
            >
              Alerts
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            icon={<FileText aria-hidden="true" />}
            aria-pressed={panel === 'reports' || (panel === 'report' && pastReport !== null)}
            onClick={() => (panel === 'reports' ? closePanel() : openPanel('reports'))}
          >
            Reports
          </Button>
          <Button
            variant="ghost"
            size="sm"
            icon={<History aria-hidden="true" />}
            aria-pressed={panel === 'history'}
            onClick={() => (panel === 'history' ? closePanel() : openPanel('history'))}
          >
            What changed
          </Button>
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
              {pastReport ? (
                <Button
                  variant="ghost"
                  size="sm"
                  icon={<ArrowLeft aria-hidden="true" />}
                  onClick={() => openPanel('reports')}
                >
                  All reports
                </Button>
              ) : null}
              <h2 id="panel-title" className={styles.panelTitle}>
                {pastReport ? 'Past report' : PANEL_TITLE[panel]}
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
            ) : panel === 'reports' ? (
              <ReportList
                onOpen={(r) => {
                  // The newest entry is the live report, with its confirm and run actions.
                  setPastReport(r.id === report.data?.id ? null : r);
                  setPanel('report');
                }}
              />
            ) : pastReport ? (
              <ReportView
                report={pastReport}
                isPending={false}
                error={null}
                onRetry={() => undefined}
                diff={null}
                archived
              />
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
