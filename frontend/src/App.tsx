import { useQueryClient } from "@tanstack/react-query";
import { PanelLeft, RefreshCw, SlidersHorizontal, SquarePen, X } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import styles from "./App.module.css";
import { keys, useChat, useLatestReport, useProfile, useSendMessage } from "./api/hooks/queries";
import { type StreamStatus, useEvents } from "./api/hooks/useEvents";
import type { Alert, ChatMessage, Report } from "./api/types";
import { nameResearch, startResearch, switchResearch, workspaceId } from "./api/workspace";
import { Button } from "./components/Button";
import { Logo } from "./components/Logo";
import { Skeleton } from "./components/Skeleton";
import { usePresence } from "./components/usePresence";
import { AlertCard } from "./features/alerts/AlertCard";
import { DEFAULT_DEMO_FIXTURE, DemoAlertButton } from "./features/alerts/DemoAlertButton";
import { askNotificationPermission } from "./features/alerts/notify";
import { useAlertDelivery } from "./features/alerts/useAlertDelivery";
import { ChatPanel } from "./features/chat/ChatPanel";
import { focusComposer } from "./features/chat/useComposerFocus";
import { CoachCard } from "./features/demo/CoachCard";
import { DemoLauncher } from "./features/demo/DemoLauncher";
import { useDemo, useGuideLocked } from "./features/demo/DemoRoot";
import { GuideLock } from "./features/demo/GuideLock";
import { ProfileHistory } from "./features/profile/ProfileHistory";
import { ReportOutline } from "./features/report/ReportOutline";
import { ReportSidebar, reportKey } from "./features/report/ReportSidebar";
import { ReportView } from "./features/report/ReportView";
import { useReportChanges } from "./features/report/useReportChanges";
import { useReportRewriting } from "./features/report/useReportRewriting";
import { ResearchList } from "./features/research/ResearchList";
import { useResearches } from "./features/research/useResearches";

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
const isNarrow = () => window.matchMedia?.(NARROW).matches ?? false;

// The demo trigger shows with the fake API, or with ?demo (fixture name: ?demo=<name>).
function demoFixture(): string | null {
  const param = new URLSearchParams(location.search).get("demo");
  if (param !== null) return param || DEFAULT_DEMO_FIXTURE;
  return import.meta.env.VITE_FAKE_API === "1" ? DEFAULT_DEMO_FIXTURE : null;
}

/**
 * The app for the current research. Switching research remounts it with an empty query
 * cache, so nothing of the previous one (panel, alert, live walk, chat) carries over (#145).
 */
export function Grabbit() {
  const { current } = useResearches();
  return <App key={current} />;
}

/** Links and SVG buttons ignore a disabled fieldset; the guided demo holds them here. */
function isHeld(target: EventTarget | null): boolean {
  if (!(target instanceof Element)) return false;
  return Boolean(
    target.closest("[data-guide-locked]") && target.closest('a[href], [role="button"]'),
  );
}

function holdLocked(e: React.MouseEvent) {
  if (!isHeld(e.target)) return;
  e.preventDefault();
  e.stopPropagation();
}

function holdLockedKey(e: React.KeyboardEvent) {
  if ((e.key === "Enter" || e.key === " ") && isHeld(e.target)) {
    e.preventDefault();
    e.stopPropagation();
  }
}

export function App() {
  const [panel, setPanel] = useState<Panel | null>(null);
  const [demo] = useState(demoFixture);
  // Inside the guided demo (#184): sample data, nothing may touch the visitor's research.
  const guided = useDemo()?.active ?? false;
  // In the guided demo the guide card makes every move; the app's own controls wait.
  const guideLocked = useGuideLocked();
  const [alertsDelivered, setAlertsDelivered] = useState(0);
  const [confirmed, setConfirmed] = useState(false);
  const report = useLatestReport();
  const diff = useReportChanges(report.data ?? undefined);
  const profile = useProfile();
  // The turn ends before the background rebuild lands; until then the report says so.
  const rewriting = useReportRewriting(profile.data, report.data);
  const send = useSendMessage({ sandbox: guided });
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
  const composer = useRef<HTMLTextAreaElement>(null);
  // Wide screens: the sidebar sits beside the chat and can collapse. Narrow: it is a drawer.
  const [sidebarOpen, setSidebarOpen] = useState(readSidebarOpen);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const research = useResearches();

  // A research from before the list existed takes its name from its first message.
  const firstAsk = chat.data?.find((m) => m.role === "user")?.text;
  useEffect(() => {
    if (firstAsk && !guided) nameResearch(firstAsk);
  }, [firstAsk, guided]);

  /** Leaves this research: every cached query belongs to it, so none may survive. */
  const leave = (go: () => void) => {
    const before = workspaceId();
    go();
    setDrawerOpen(false);
    if (workspaceId() !== before) client.clear();
  };
  // A fresh research remounts the chat, which focuses its box; an unused one is reused as is.
  const newResearch = () => {
    leave(startResearch);
    focusComposer(composer.current);
  };
  const openResearch = (id: string) => leave(() => switchResearch(id));
  const newResearchRef = useRef(newResearch);
  newResearchRef.current = newResearch;

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
    // Opened by the app, or from a control that is gone since: the message box takes over.
    const back = returnFocus.current;
    returnFocus.current = null;
    if (back?.isConnected) back.focus();
    else focusComposer(composer.current);
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
  const deliverAlert = useAlertDelivery(showAlert, { desktop: !guided });
  const deliver = useCallback(
    (alert: Alert) => {
      deliverAlert(alert);
      setAlertsDelivered((n) => n + 1);
    },
    [deliverAlert],
  );
  const stream = useEvents(deliver);

  // Opened by the app, not by the reader: focus moves without a focus frame around it.
  const openedByApp = useRef(false);
  // Opened from the sidebar's reports: the reader keeps working in the message box.
  const openedFromSidebar = useRef(false);

  // A rewrite is the moment to watch: open the report on the change.
  useEffect(() => {
    if (!diff) return;
    setPastReport(null);
    openedByApp.current = true;
    setPanel("report");
  }, [diff]);

  // The demo waits for the visitor to open the report before it explains the badges.
  const [reportOpened, setReportOpened] = useState(false);
  useEffect(() => {
    if (guided && panel === "report") setReportOpened(true);
  }, [guided, panel]);

  useEffect(() => {
    if (!panel) return;
    // A rewrite opening the report never takes the message box from someone typing in it.
    const typing = openedByApp.current && document.activeElement === composer.current;
    // `focusVisible: false` keeps the ring for keyboard opens only (supported in Chromium).
    if (!typing && !openedFromSidebar.current)
      panelRef.current?.focus(
        openedByApp.current ? ({ focusVisible: false } as FocusOptions) : undefined,
      );
    openedByApp.current = false;
    openedFromSidebar.current = false;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") closePanel();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [panel, closePanel]);

  // Ctrl/Cmd+Shift+O starts a new research, as in other chat apps.
  useEffect(() => {
    if (guided) return;
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "o") {
        e.preventDefault();
        newResearchRef.current();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [guided]);

  useEffect(() => {
    if (!drawerOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setDrawerOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [drawerOpen]);

  const openReport = (r: Report, latest: boolean) => {
    // On narrow screens the panel covers the chat, so it takes focus as usual. Wide, the
    // message box keeps it, and closing the panel comes back to it.
    if (isNarrow()) {
      if (document.activeElement instanceof HTMLElement)
        returnFocus.current = document.activeElement;
    } else {
      returnFocus.current = null;
      openedFromSidebar.current = panel !== "report";
      focusComposer(composer.current);
    }
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
    if (!guided) void askNotificationPermission();
    send.mutate(CONFIRM_MESSAGE);
  };

  const coach = (submit: (text: string) => void, busy: boolean) => (
    <CoachCard
      signals={{
        agentReplies: messages.filter((m) => m.role === "agent").length,
        hasReport: Boolean(report.data),
        reportOpened,
        profileVersion: profile.data?.version ?? 0,
        alerts: alertsDelivered,
      }}
      actions={{
        send: submit,
        openReport: () => openPanel("report"),
        confirm: () => {
          setConfirmed(true);
          submit(CONFIRM_MESSAGE);
        },
      }}
      busy={busy}
      floating={panel !== null}
    />
  );

  const reportInChat = report.isPending ? (
    <Skeleton block="card" label="Loading the report" />
  ) : report.data ? (
    <GuideLock>
      <ReportOutline
        key={report.data.id}
        report={report.data}
        open={panel === "report" && pastReport === null}
        rewriting={rewriting}
        rewritten={diff !== null}
        onOpen={() => openPanel("report")}
      />
    </GuideLock>
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
  // While it rewrites, the outline waits under the turn that asked for the new report.
  const lastLinked = messages.findLast((m) => m.role === "agent" && m.report_id);
  const reportAnchor =
    (rewriting && lastLinked && lastLinked.report_id !== report.data?.id && lastLinked.id) ||
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
      data-guided={guided || undefined}
      onClickCapture={guided ? holdLocked : undefined}
      onKeyDownCapture={guided ? holdLockedKey : undefined}
    >
      <GuideLock>
        <ReportSidebar
          id="report-sidebar"
          className={styles.sidebar}
          activeKey={activeKey}
          onOpen={openReport}
          onClose={closeSidebar}
          brand={<Logo />}
          top={
            guided ? undefined : (
              <ResearchList
                current={research.current}
                list={research.list}
                onNew={newResearch}
                onOpen={openResearch}
              />
            )
          }
          foot={guided ? undefined : <DemoLauncher place="sidebar" />}
        />
      </GuideLock>
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
            icon={<PanelLeft aria-hidden="true" />}
            disabled={guideLocked}
            onClick={openSidebar}
          />
          <span className={styles.topLogo} aria-hidden="true">
            <Logo />
          </span>
          <span className={styles.status} data-status={stream} role="status">
            <span className={styles.statusLabel}>{STATUS_TEXT[stream]}</span>
          </span>
          <div className={styles.actions}>
            {demo && !guided && (
              <DemoAlertButton fixture={demo} labelClassName={styles.actionLabel} />
            )}
            {!guided && (
              <Button
                variant="ghost"
                size="sm"
                className={styles.newResearch}
                aria-keyshortcuts="Control+Shift+O Meta+Shift+O"
                title="New research (Ctrl+Shift+O)"
                icon={<SquarePen aria-hidden="true" />}
                onClick={newResearch}
              >
                <span className={styles.actionLabel}>New research</span>
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              icon={<SlidersHorizontal aria-hidden="true" />}
              aria-pressed={panel === "history"}
              disabled={guideLocked}
              onClick={() => (panel === "history" ? closePanel() : openPanel("history"))}
            >
              <span className={styles.actionLabel}>What changed</span>
            </Button>
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
              followKey={`${report.data?.id}|${reportAnchor}|${openAlert?.alert.id}|${rewriting}`}
              coach={guided ? coach : undefined}
              composerRef={composer}
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
                    rewriting={rewriting}
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
