import { useQueryClient } from "@tanstack/react-query";
import { History, PanelLeftOpen, RefreshCw, X } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import styles from "./App.module.css";
import { keys, useChat, useLatestReport, useSendMessage } from "./api/hooks/queries";
import { type StreamStatus, useEvents } from "./api/hooks/useEvents";
import type { Alert, ChatMessage, Report } from "./api/types";
import { Button } from "./components/Button";
import { FullscreenButton } from "./components/FullscreenButton";
import { Logo } from "./components/Logo";
import { Skeleton } from "./components/Skeleton";
import { usePresence } from "./components/usePresence";
import { AlertCard } from "./features/alerts/AlertCard";
import { DEFAULT_DEMO_FIXTURE, DemoAlertButton } from "./features/alerts/DemoAlertButton";
import { askNotificationPermission } from "./features/alerts/notify";
import { useAlertDelivery } from "./features/alerts/useAlertDelivery";
import { ChatPanel } from "./features/chat/ChatPanel";
import { ProfileHistory } from "./features/profile/ProfileHistory";
import { ReportOutline } from "./features/report/ReportOutline";
import { ReportSidebar, reportKey } from "./features/report/ReportSidebar";
import { ReportView } from "./features/report/ReportView";
import { useReportChanges } from "./features/report/useReportChanges";

type Panel = "report" | "history";

const PANEL_TITLE: Record<Panel, string> = { report: "Report", history: "What changed" };

// The sidebar's open or closed state is a per-browser convenience; it may be unavailable.
const SIDEBAR_KEY = "grabbit.sidebar";
function readSidebarOpen(): boolean {
  try {
    return localStorage.getItem(SIDEBAR_KEY) !== "closed";
  } catch {
    return true;
  }
}
function saveSidebarOpen(open: boolean) {
  try {
    localStorage.setItem(SIDEBAR_KEY, open ? "open" : "closed");
  } catch {
    // Private mode or blocked storage: the sidebar still works, it only forgets.
  }
}

export { ALERT_DELAY_MS } from "./features/alerts/DemoAlertButton";

export const CONFIRM_MESSAGE = "Looks right, keep me posted.";

const STATUS_TEXT: Record<StreamStatus, string> = {
  connecting: "Connecting",
  open: "Live",
  retrying: "Reconnecting",
};

// Below this width the panel covers the chat and the sidebar becomes a drawer.
const NARROW = "(max-width: 63.99rem)";

// The demo trigger shows with the fake API, or with ?demo (fixture name: ?demo=<name>).
function demoFixture(): string | null {
  const param = new URLSearchParams(location.search).get("demo");
  if (param !== null) return param || DEFAULT_DEMO_FIXTURE;
  return import.meta.env.VITE_FAKE_API === "1" ? DEFAULT_DEMO_FIXTURE : null;
}

export function App() {
  const [panel, setPanel] = useState<Panel | null>(null);
  const [demo] = useState(demoFixture);
  const [confirmed, setConfirmed] = useState(false);
  const report = useLatestReport();
  const diff = useReportChanges(report.data ?? undefined);
  const send = useSendMessage();
  const client = useQueryClient();
  const chat = useChat();
  // An opened alert stays where it was opened: after the last message at that moment.
  const [openAlert, setOpenAlert] = useState<{ alert: Alert; after: string | null } | null>(null);
  // A past report opened from the sidebar; null shows the latest one.
  const [pastReport, setPastReport] = useState<Report | null>(null);
  const panelRef = useRef<HTMLElement>(null);
  // The panel slides out before it unmounts; `shownPanel` holds what it showed meanwhile.
  const { shown: shownPanel, leaving: panelLeaving } = usePresence(panel, panelRef);
  const returnFocus = useRef<HTMLElement | null>(null);
  // Wide screens: the sidebar sits beside the chat and can collapse. Narrow: it is a drawer.
  const [sidebarOpen, setSidebarOpen] = useState(readSidebarOpen);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const isNarrow = () => window.matchMedia?.(NARROW).matches ?? false;

  const openSidebar = () => {
    if (isNarrow()) return setDrawerOpen(true);
    setSidebarOpen(true);
    saveSidebarOpen(true);
  };
  const closeSidebar = () => {
    if (isNarrow()) return setDrawerOpen(false);
    setSidebarOpen(false);
    saveSidebarOpen(false);
  };

  const openPanel = useCallback((next: Panel) => {
    if (document.activeElement instanceof HTMLElement) returnFocus.current = document.activeElement;
    setPastReport(null);
    setPanel(next);
  }, []);

  const closePanel = useCallback(() => {
    setPanel(null);
    returnFocus.current?.focus();
  }, []);

  const showAlert = useCallback(
    (alert: Alert) => {
      const shown = client.getQueryData<ChatMessage[]>(keys.chat) ?? [];
      setOpenAlert({ alert, after: shown.at(-1)?.id ?? null });
      // The alert opens in the chat; on narrow screens the panel would hide it.
      if (window.matchMedia?.(NARROW).matches) setPanel(null);
    },
    [client],
  );
  const deliver = useAlertDelivery(showAlert);
  const stream = useEvents(deliver);

  // A rewrite is the moment to watch: open the report on the change.
  useEffect(() => {
    if (!diff) return;
    setPastReport(null);
    setPanel("report");
  }, [diff]);

  useEffect(() => {
    if (!panel) return;
    panelRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") closePanel();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [panel, closePanel]);

  useEffect(() => {
    if (!drawerOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setDrawerOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [drawerOpen]);

  const openReport = (r: Report, latest: boolean) => {
    if (document.activeElement instanceof HTMLElement) returnFocus.current = document.activeElement;
    // The latest entry is the live report, with its confirm and run actions.
    setPastReport(latest ? null : r);
    setPanel("report");
    setDrawerOpen(false);
  };

  const activeKey =
    panel !== "report"
      ? null
      : pastReport
        ? reportKey(pastReport)
        : report.data
          ? reportKey(report.data)
          : null;

  const confirm = () => {
    setConfirmed(true);
    void askNotificationPermission();
    send.mutate(CONFIRM_MESSAGE);
  };

  const reportInChat = report.isPending ? (
    <Skeleton block="card" label="Loading the report" />
  ) : report.data ? (
    <ReportOutline
      key={report.data.id}
      report={report.data}
      open={panel === "report" && pastReport === null}
      rewritten={diff !== null}
      onOpen={() => openPanel("report")}
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

  // The outline follows the agent turn that wrote this report; a report from elsewhere
  // (Run now, the schedule) has no such turn and goes after the conversation.
  const messages = chat.data ?? [];
  const reportAnchor =
    (report.data &&
      messages.findLast((m) => m.role === "agent" && m.report_id === report.data?.id)?.id) ||
    null;
  const alertAnchored = Boolean(openAlert?.after && messages.some((m) => m.id === openAlert.after));
  const alertInChat = openAlert && (
    <AlertCard alert={openAlert.alert} onClose={() => setOpenAlert(null)} />
  );

  return (
    <div
      className={styles.app}
      data-sidebar={sidebarOpen ? "open" : "closed"}
      data-drawer={drawerOpen ? "open" : undefined}
    >
      <ReportSidebar
        id="report-sidebar"
        className={styles.sidebar}
        activeKey={activeKey}
        onOpen={openReport}
        onClose={closeSidebar}
        brand={<Logo />}
      />
      {drawerOpen && (
        <button
          type="button"
          className={styles.scrim}
          aria-label="Close sidebar"
          tabIndex={-1}
          onClick={() => setDrawerOpen(false)}
        />
      )}

      <div className={styles.workspace}>
        <header className={styles.topbar}>
          {/* One page heading whichever logo is visible. */}
          <h1 className="visually-hidden">Grabbit</h1>
          <Button
            variant="ghost"
            size="sm"
            className={styles.openSidebar}
            aria-label="Open sidebar"
            aria-controls="report-sidebar"
            aria-expanded={drawerOpen}
            icon={<PanelLeftOpen aria-hidden="true" />}
            onClick={openSidebar}
          />
          <span className={styles.topLogo} aria-hidden="true">
            <Logo />
          </span>
          <span className={styles.status} data-status={stream} role="status">
            {STATUS_TEXT[stream]}
          </span>
          <div className={styles.actions}>
            {demo && <DemoAlertButton fixture={demo} labelClassName={styles.actionLabel} />}
            <Button
              variant="ghost"
              size="sm"
              icon={<History aria-hidden="true" />}
              aria-pressed={panel === "history"}
              onClick={() => (panel === "history" ? closePanel() : openPanel("history"))}
            >
              <span className={styles.actionLabel}>What changed</span>
            </Button>
            <FullscreenButton />
          </div>
        </header>

        <main className={styles.main} data-panel={shownPanel ?? undefined}>
          <div className={styles.chat}>
            <ChatPanel
              renderAfter={(m) => (
                <>
                  {m.id === reportAnchor && reportInChat}
                  {alertAnchored && m.id === openAlert?.after && alertInChat}
                </>
              )}
              footer={
                <>
                  {!reportAnchor && reportInChat}
                  {!alertAnchored && alertInChat}
                </>
              }
              followKey={`${report.data?.id}|${reportAnchor}|${openAlert?.alert.id}`}
            />
          </div>
          {shownPanel && (
            <section
              ref={panelRef}
              data-state={panelLeaving ? "leaving" : undefined}
              aria-hidden={panelLeaving || undefined}
              id="report-panel"
              className={styles.panel}
              aria-labelledby="panel-title"
              // biome-ignore lint/a11y/noNoninteractiveTabindex: a scrollable region needs keyboard focus (axe scrollable-region-focusable).
              tabIndex={0}
            >
              <div className={styles.panelBar}>
                <h2 id="panel-title" className={styles.panelTitle}>
                  {pastReport ? "Past report" : PANEL_TITLE[shownPanel]}
                </h2>
                <Button
                  variant="ghost"
                  size="sm"
                  aria-label="Close panel"
                  icon={<X aria-hidden="true" />}
                  onClick={closePanel}
                />
              </div>
              <div
                key={pastReport ? `past-${reportKey(pastReport)}` : shownPanel}
                className={styles.panelContent}
              >
                {shownPanel === "history" ? (
                  <ProfileHistory />
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
                    report={report.data ?? undefined}
                    isPending={report.isPending}
                    error={report.error}
                    onRetry={() => report.refetch()}
                    diff={diff}
                    onConfirm={confirm}
                    confirmed={confirmed}
                  />
                )}
              </div>
            </section>
          )}
        </main>
      </div>
    </div>
  );
}
