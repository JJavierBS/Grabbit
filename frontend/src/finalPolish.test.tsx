import { act, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { App } from "./App";
import type { ChatMessage } from "./api/types";
import { Markdown } from "./components/Markdown";
import { chatV2, historyV2, profileV2, reportV1, reportV2 } from "./dev/fixtures";
import { mockApi, renderWithClient } from "./test/renderApp";

describe("agent prose reads like prose", () => {
  it("writes raw amounts compactly, as the report's facts do", () => {
    const { container } = render(
      <Markdown source="FIRSTPICK led a 650000 EUR round; Palette raised 3000000 EUR and Pally 5200000 USD." />,
    );
    expect(container).toHaveTextContent(
      "FIRSTPICK led a €650K round; Palette raised €3M and Pally $5.2M.",
    );
  });

  it("leaves small numbers, years and team sizes alone", () => {
    const { container } = render(<Markdown source="Founded in 2019 with 12 people; 36 raised." />);
    expect(container).toHaveTextContent("Founded in 2019 with 12 people; 36 raised.");
  });

  it("drops the leading zero from written-out days", () => {
    const { container } = render(<Markdown source="Compuvi raised on 01 Jul 2025, not 10 Jul." />);
    expect(container).toHaveTextContent("Compuvi raised on 1 Jul 2025, not 10 Jul.");
  });
});

describe("panel focus", () => {
  const base = {
    "GET /api/profile": () => profileV2,
    "GET /api/profile/history": () => historyV2,
    "GET /api/chat": () => chatV2,
    "GET /api/alerts": () => [],
    "GET /api/reports": () => [],
  };

  afterEach(() => vi.restoreAllMocks());

  const reply: ChatMessage = {
    id: "m9",
    role: "agent",
    report_id: null,
    ui: null,
    graph: null,
    walk: null,
    sources: [],
    questions: [],
    text: "I rewrote your report.",
    created_at: "2026-11-14T09:34:00Z",
    profile_changes: [],
  };

  it("moves focus to a panel the app opened without drawing the focus frame", async () => {
    let report = reportV1;
    const api = mockApi({ ...base, "GET /api/reports/latest": () => report });
    const focus = vi.spyOn(HTMLElement.prototype, "focus");
    renderWithClient(<App />);
    await screen.findByRole("button", { name: "Open report" });

    // A background rebuild lands while the reader is elsewhere on the page.
    act(() => (document.activeElement as HTMLElement | null)?.blur());
    report = reportV2;
    api.streams.at(-1)?.push("report", {});
    await screen.findByText(/Rewritten for you/);
    const panel = document.getElementById("report-panel");
    const panelCalls = focus.mock.contexts
      .map((ctx, i) => [ctx, focus.mock.calls[i][0]] as const)
      .filter(([ctx]) => ctx === panel);
    expect(panelCalls.at(-1)?.[1]).toEqual({ focusVisible: false });
  });

  it("leaves focus in the message box when the app opens the panel (#188)", async () => {
    let report = reportV1;
    mockApi({
      ...base,
      "GET /api/reports/latest": () => report,
      "POST /api/chat": () => {
        report = reportV2;
        return reply;
      },
    });
    renderWithClient(<App />);
    await screen.findByRole("button", { name: "Open report" });
    const box = screen.getByRole("textbox", { name: "Message Grabbit" });

    await userEvent.type(box, "Shorter, co-investors first{Enter}");
    await screen.findByText(/Rewritten for you/);
    expect(document.getElementById("report-panel")).toBeInTheDocument();
    expect(box).toHaveFocus();
  });

  it("keeps the message box focused when a report opens from the sidebar (#188)", async () => {
    mockApi({
      ...base,
      "GET /api/reports/latest": () => reportV2,
      "GET /api/reports": () => [reportV2, reportV1],
    });
    renderWithClient(<App />);
    const nav = screen.getByRole("navigation", { name: "Reports" });
    const items = await within(nav).findAllByRole("button");

    await userEvent.click(items[1]);
    expect(screen.getByRole("region", { name: "Past report" })).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Message Grabbit" })).toHaveFocus();

    await userEvent.click(items[0]);
    expect(screen.getByRole("region", { name: "Report" })).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Message Grabbit" })).toHaveFocus();

    await userEvent.keyboard("{Escape}");
    expect(screen.getByRole("textbox", { name: "Message Grabbit" })).toHaveFocus();
  });

  it("keeps the focus frame when the reader opens the panel", async () => {
    mockApi({ ...base, "GET /api/reports/latest": () => reportV1 });
    const focus = vi.spyOn(HTMLElement.prototype, "focus");
    renderWithClient(<App />);
    await userEvent.click(await screen.findByRole("button", { name: "Open report" }));
    const panel = document.getElementById("report-panel");
    const i = focus.mock.contexts.lastIndexOf(panel as HTMLElement);
    expect(i).toBeGreaterThanOrEqual(0);
    expect(focus.mock.calls[i][0]).toBeUndefined();
  });
});
