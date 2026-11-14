import { act, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ALERT_DELAY_MS, App, CONFIRM_MESSAGE } from "./App";
import type { ChatMessage } from "./api/types";
import { chatV2, historyV2, profileV2, reportV1, reportV2 } from "./dev/fixtures";
import { MIC_BLOCKED, NOT_TRANSCRIBED, NOTHING_HEARD } from "./features/chat/useDictation";
import { formatChangeValue } from "./features/profile/ProfileHistory";
import { shortTitle } from "./features/report/ReportSidebar";
import { mockApi, renderWithClient } from "./test/renderApp";

const base = {
  "GET /api/profile": () => profileV2,
  "GET /api/profile/history": () => historyV2,
  "GET /api/chat": () => chatV2,
  "GET /api/alerts": () => [],
  "GET /api/reports": () => [],
};

describe("App", () => {
  it("omits the fullscreen action even when the browser supports it", async () => {
    const descriptor = Object.getOwnPropertyDescriptor(document, "fullscreenEnabled");
    Object.defineProperty(document, "fullscreenEnabled", { configurable: true, value: true });
    try {
      mockApi({ ...base, "GET /api/reports/latest": () => reportV1 });
      renderWithClient(<App />);
      expect(await screen.findByRole("button", { name: "What changed" })).toBeInTheDocument();
      expect(screen.queryByRole("button", { name: /full screen/i })).not.toBeInTheDocument();
    } finally {
      if (descriptor) Object.defineProperty(document, "fullscreenEnabled", descriptor);
      else Reflect.deleteProperty(document, "fullscreenEnabled");
    }
  });

  it("shows the report as an outline in the chat, then opens it in the side panel", async () => {
    mockApi({ ...base, "GET /api/reports/latest": () => reportV1 });
    renderWithClient(<App />);
    expect(await screen.findByText(/Tell me what you look for/)).toBeInTheDocument();
    const outline = await screen.findByRole("article", { name: "Slush 2026 prep report outline" });
    expect(
      within(outline).getByText(new RegExp(`${reportV1.candidates.length} startups`)),
    ).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Northwind Labs" })).not.toBeInTheDocument();

    await userEvent.click(within(outline).getByRole("button", { name: "Open report" }));
    const panel = screen.getByRole("region", { name: "Report" });
    expect(
      within(panel).getByRole("heading", { name: "Slush 2026 prep report" }),
    ).toBeInTheDocument();
    expect(within(panel).getByRole("heading", { name: "Northwind Labs" })).toBeInTheDocument();
    expect(within(panel).getAllByText("Official filing").length).toBeGreaterThan(0);

    await userEvent.keyboard("{Escape}");
    expect(screen.queryByRole("region", { name: "Report" })).not.toBeInTheDocument();
    expect(within(outline).getByRole("button", { name: "Open report" })).toHaveFocus();
  });

  it("closes the side panel with its close button", async () => {
    mockApi({ ...base, "GET /api/reports/latest": () => reportV1 });
    renderWithClient(<App />);
    await userEvent.click(await screen.findByRole("button", { name: "Open report" }));
    await userEvent.click(screen.getByRole("button", { name: "Close panel" }));
    expect(screen.queryByRole("region", { name: "Report" })).not.toBeInTheDocument();
  });

  it("welcomes an empty chat with the logo and wordmark, gone once there is a message", async () => {
    mockApi({ ...base, "GET /api/chat": () => [], "GET /api/reports/latest": () => reportV1 });
    const { unmount } = renderWithClient(<App />);
    const log = await screen.findByRole("log");
    expect(await within(log).findByText("Grabbit")).toBeInTheDocument();
    unmount();

    mockApi({ ...base, "GET /api/reports/latest": () => reportV1 });
    renderWithClient(<App />);
    expect(await screen.findByText(/Tell me what you look for/)).toBeInTheDocument();
    expect(within(screen.getByRole("log")).queryByText("Grabbit")).not.toBeInTheDocument();
  });

  it("shows no error before the first report exists", async () => {
    mockApi({
      ...base,
      "GET /api/reports/latest": {
        status: 404,
        body: { error: { code: "no_report", message: "No report has been generated yet." } },
      },
    });
    renderWithClient(<App />);
    expect(await screen.findByText(/Tell me what you look for/)).toBeInTheDocument();
    await act(() => new Promise((resolve) => setTimeout(resolve, 50)));
    expect(screen.queryByText("The report did not load")).not.toBeInTheDocument();
    expect(screen.queryByText("No report has been generated yet.")).not.toBeInTheDocument();
  });

  it("renders the agent's Markdown instead of showing asterisks", async () => {
    const reply: ChatMessage = {
      id: "m-md",
      role: "agent",
      text: "**GREÏ** (Pre-Seed): lead FIRSTPICK.\n\n- Raise soon?\n- Small teams?",
      created_at: "2026-11-14T09:00:00Z",
      profile_changes: [],
      report_id: null,
      ui: null,
      graph: null,
      walk: null,
      sources: [],
      questions: [],
    };
    mockApi({ ...base, "GET /api/chat": () => [reply], "GET /api/reports/latest": () => reportV1 });
    renderWithClient(<App />);
    expect(await screen.findByText("GREÏ", { selector: "strong" })).toBeInTheDocument();
    expect(screen.queryByText(/\*\*/)).not.toBeInTheDocument();
    expect(screen.getByText("Small teams?", { selector: "li" })).toBeInTheDocument();
  });

  it("shows an error with a retry when the report fails, never a blank screen", async () => {
    mockApi({
      ...base,
      "GET /api/reports/latest": {
        status: 500,
        body: { error: { code: "boom", message: "Cala timed out." } },
      },
    });
    renderWithClient(<App />);
    expect(await screen.findByText("The report did not load")).toBeInTheDocument();
    expect(screen.getByText("Cala timed out.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
  });

  it("highlights what changed when a correction rewrites the report", async () => {
    let report = reportV1;
    const reply: ChatMessage = {
      id: "m9",
      role: "agent",
      report_id: null,
      ui: null,
      graph: null,
      walk: null,
      sources: [],
      questions: [],
      text: "From now on: shorter reports, co-investors first. I rewrote your report.",
      created_at: "2026-11-14T09:34:00Z",
      profile_changes: [],
    };
    const calls = mockApi({
      ...base,
      "GET /api/reports/latest": () => report,
      "POST /api/chat": () => {
        report = reportV2;
        return reply;
      },
    });
    renderWithClient(<App />);
    await screen.findByRole("button", { name: "Open report" });

    await userEvent.type(
      screen.getByRole("textbox", { name: "Message Grabbit" }),
      "Shorter, co-investors first{Enter}",
    );

    const banner = await screen.findByText(/Rewritten for you/);
    expect(banner.parentElement).toHaveTextContent("2 sections moved");
    expect(screen.getByText("Rounds and leads").tagName).toBe("S");
    const section = screen
      .getByRole("heading", { name: "Co-investors you trust" })
      .closest("section");
    expect(section).toHaveAttribute("data-changed", "moved");
    expect(within(section as HTMLElement).getByText("Moved")).toBeInTheDocument();
    expect(calls.find((c) => c.key === "POST /api/chat")?.body).toEqual({
      text: "Shorter, co-investors first",
    });
  });

  it("confirms the report by telling the agent and asking for notifications", async () => {
    const requestPermission = vi.fn(async () => "granted");
    vi.stubGlobal("Notification", { permission: "default", requestPermission });
    const calls = mockApi({
      ...base,
      "GET /api/reports/latest": () => reportV1,
      "POST /api/chat": () => ({ ...chatV2[0], id: "m10" }),
    });
    renderWithClient(<App />);
    await userEvent.click(await screen.findByRole("button", { name: "Open report" }));
    await userEvent.click(screen.getByRole("button", { name: "Looks right, keep me posted" }));
    expect(calls.find((c) => c.key === "POST /api/chat")?.body).toEqual({ text: CONFIRM_MESSAGE });
    expect(await screen.findByRole("button", { name: "Watching your shortlist" })).toBeDisabled();
    expect(requestPermission).toHaveBeenCalledOnce();
    vi.unstubAllGlobals();
  });

  it("opens an alert from the event stream in the chat, labelled as simulated", async () => {
    const calls = mockApi({ ...base, "GET /api/reports/latest": () => reportV1 });
    renderWithClient(<App />);
    await screen.findByRole("button", { name: "Open report" });
    calls.streams[0].open();
    calls.streams[0].push("alert", {
      id: "al-7",
      created_at: "2026-11-14T10:00:00Z",
      entity_id: "c-northwind",
      entity_name: "Northwind Labs",
      kind: "new_round",
      title: "Northwind Labs is raising a Series A",
      why_it_matters: "Aurora Ventures leads it.",
      importance: 0.9,
      facts: [],
      simulated: true,
    });
    await userEvent.click(screen.getByRole("button", { name: "Open in chat" }));
    const card = screen.getByRole("article", { name: "Northwind Labs is raising a Series A" });
    expect(within(card).getByText("Simulated event")).toBeInTheDocument();
    expect(within(card).getByText("Aurora Ventures leads it.")).toBeInTheDocument();
    expect(screen.getByText("Live")).toBeInTheDocument();
  });

  it("lists past reports in the sidebar and opens one read only", async () => {
    mockApi({
      ...base,
      "GET /api/reports/latest": () => reportV2,
      "GET /api/reports": () => [reportV2, reportV1],
    });
    renderWithClient(<App />);
    const nav = screen.getByRole("navigation", { name: "Reports" });
    const items = await within(nav).findAllByRole("button");
    expect(items).toHaveLength(2);
    expect(items[0]).toHaveTextContent(shortTitle(reportV2));
    expect(items[0]).toHaveAttribute("title", reportV2.summary);
    expect(items[0]).toHaveTextContent("Latest");
    // The time follows the browser locale: "09:34" or "09:34 AM".
    expect(items[0]).toHaveTextContent(/ startups · \d{1,2}[:.]\d{2}/);
    expect(items[0].textContent).not.toMatch(/\bv\d/);

    await userEvent.click(items[1]);
    const past = screen.getByRole("region", { name: "Past report" });
    expect(within(past).getByText(reportV1.summary)).toBeInTheDocument();
    expect(within(past).queryByRole("button", { name: "Run now" })).not.toBeInTheDocument();
    expect(items[1]).toHaveAttribute("aria-current", "true");

    await userEvent.click(items[0]);
    const latest = screen.getByRole("region", { name: "Report" });
    expect(within(latest).getByRole("button", { name: "Run now" })).toBeInTheDocument();
    expect(items[0]).toHaveAttribute("aria-current", "true");
    expect(items[1]).not.toHaveAttribute("aria-current");
  });

  it("remembers a collapsed sidebar", async () => {
    localStorage.clear();
    mockApi({ ...base, "GET /api/reports/latest": () => reportV1 });
    const first = renderWithClient(<App />);
    const shell = first.container.firstElementChild as HTMLElement;
    expect(shell).toHaveAttribute("data-sidebar", "open");
    await userEvent.click(screen.getByRole("button", { name: "Close sidebar" }));
    expect(shell).toHaveAttribute("data-sidebar", "closed");
    first.unmount();

    const second = renderWithClient(<App />);
    expect(second.container.firstElementChild).toHaveAttribute("data-sidebar", "closed");
    await userEvent.click(screen.getByRole("button", { name: "Open sidebar" }));
    expect(second.container.firstElementChild).toHaveAttribute("data-sidebar", "open");
    localStorage.clear();
  });

  it("fires the staged GREÏ alert 30 s after Alerts is pressed, with no demo data label", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    window.history.replaceState({}, "", "/?demo");
    const calls = mockApi({
      ...base,
      "GET /api/reports/latest": () => reportV1,
      "POST /api/demo/simulate-event": () => ({}),
    });
    renderWithClient(<App />);
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    const button = await screen.findByRole("button", { name: "Alerts" });
    expect(screen.queryByText(/Demo data/)).not.toBeInTheDocument();

    await user.click(button);
    expect(button).toBeDisabled();
    act(() => vi.advanceTimersByTime(ALERT_DELAY_MS - 1000));
    expect(calls.some((c) => c.key === "POST /api/demo/simulate-event")).toBe(false);
    act(() => vi.advanceTimersByTime(1000));
    await waitFor(() =>
      expect(calls.find((c) => c.key === "POST /api/demo/simulate-event")?.body).toEqual({
        fixture: "grei_seed_round",
      }),
    );
    window.history.replaceState({}, "", "/");
    vi.useRealTimers();
  });

  /** A microphone and recorder that hand over `audio` when stopped. */
  function stubRecorder({ denied = false } = {}) {
    const track = { stop: vi.fn() };
    const stream = { getTracks: () => [track] };
    const recorders: FakeRecorder[] = [];
    class FakeRecorder {
      state = "inactive";
      mimeType = "audio/webm;codecs=opus";
      stream = stream;
      ondataavailable: ((e: { data: Blob }) => void) | null = null;
      onstop: (() => void) | null = null;
      constructor() {
        recorders.push(this);
      }
      start() {
        this.state = "recording";
      }
      stop() {
        this.state = "inactive";
        this.ondataavailable?.({ data: new Blob(["opus"], { type: this.mimeType }) });
        this.onstop?.();
      }
    }
    vi.stubGlobal("MediaRecorder", FakeRecorder);
    Object.defineProperty(navigator, "mediaDevices", {
      configurable: true,
      value: {
        getUserMedia: vi.fn(() =>
          denied
            ? Promise.reject(new DOMException("denied", "NotAllowedError"))
            : Promise.resolve(stream),
        ),
      },
    });
    return { recorders, track };
  }

  afterEach(() => {
    vi.unstubAllGlobals();
    Reflect.deleteProperty(navigator, "mediaDevices");
  });

  it("records while Talk is on and adds what was said after the typed text", async () => {
    const { track } = stubRecorder();
    const calls = mockApi({
      ...base,
      "GET /api/reports/latest": () => reportV1,
      "POST /api/transcribe": () => ({ text: "drop consumer health" }),
    });
    renderWithClient(<App />);
    const box = await screen.findByRole("textbox", { name: "Message Grabbit" });
    await userEvent.type(box, "Shorter,");
    await userEvent.click(screen.getByRole("button", { name: "Talk" }));
    expect(await screen.findByRole("button", { name: "Stop talking" })).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Stop talking" }));
    await waitFor(() => expect(box).toHaveValue("Shorter, drop consumer health"));
    expect(track.stop).toHaveBeenCalled();
    expect(calls.some((c) => c.key === "POST /api/transcribe")).toBe(true);
    expect(screen.getByRole("button", { name: "Talk" })).toBeEnabled();
  });

  it("asks to allow the microphone when the browser blocks it", async () => {
    stubRecorder({ denied: true });
    mockApi({ ...base, "GET /api/reports/latest": () => reportV1 });
    renderWithClient(<App />);
    await userEvent.click(await screen.findByRole("button", { name: "Talk" }));
    expect(await screen.findByText(MIC_BLOCKED)).toBeInTheDocument();
  });

  it("says so when nothing was heard or the transcription fails", async () => {
    stubRecorder();
    let reply: unknown = { text: "" };
    mockApi({
      ...base,
      "GET /api/reports/latest": () => reportV1,
      "POST /api/transcribe": () => reply,
    });
    renderWithClient(<App />);
    await userEvent.click(await screen.findByRole("button", { name: "Talk" }));
    await userEvent.click(await screen.findByRole("button", { name: "Stop talking" }));
    expect(await screen.findByText(NOTHING_HEARD)).toBeInTheDocument();

    reply = undefined;
    mockApi({
      ...base,
      "GET /api/reports/latest": () => reportV1,
      "POST /api/transcribe": {
        status: 502,
        body: { error: { code: "transcription_failed", message: "x" } },
      },
    });
    await userEvent.click(screen.getByRole("button", { name: "Talk" }));
    await userEvent.click(await screen.findByRole("button", { name: "Stop talking" }));
    expect(await screen.findByText(NOT_TRANSCRIBED)).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Message Grabbit" })).toHaveValue("");
  });

  it("hides Talk when the browser cannot record", async () => {
    mockApi({ ...base, "GET /api/reports/latest": () => reportV1 });
    renderWithClient(<App />);
    await screen.findByRole("button", { name: "Open report" });
    expect(screen.queryByRole("button", { name: "Talk" })).not.toBeInTheDocument();
  });

  it("opens the profile history with the reason for each change", async () => {
    mockApi({ ...base, "GET /api/reports/latest": () => reportV1 });
    renderWithClient(<App />);
    await userEvent.click(screen.getByRole("button", { name: "What changed" }));
    expect(await screen.findByText("You said you trust these two investors.")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Plain language. One paragraph per startup. Lead with the round and who led it.",
      ),
    ).toBeInTheDocument();
  });
});

describe("formatChangeValue", () => {
  it("reads empty, lists, objects and enum values in plain words", () => {
    expect(formatChangeValue(null)).toBe("nothing");
    expect(formatChangeValue([])).toBe("nothing");
    expect(formatChangeValue(["pre_seed", "seed"])).toBe("Pre-seed, Seed");
    expect(formatChangeValue([{ entity_id: "x", name: "Aurora Ventures" }])).toBe(
      "Aurora Ventures",
    );
    expect(formatChangeValue({ value: 25000, unit: "EUR" })).toBe("25000");
  });
});
