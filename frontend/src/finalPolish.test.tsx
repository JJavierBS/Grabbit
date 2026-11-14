import { render, screen } from "@testing-library/react";
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

  it("moves focus to a panel the app opened without drawing the focus frame", async () => {
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
      text: "I rewrote your report.",
      created_at: "2026-11-14T09:34:00Z",
      profile_changes: [],
    };
    mockApi({
      ...base,
      "GET /api/reports/latest": () => report,
      "POST /api/chat": () => {
        report = reportV2;
        return reply;
      },
    });
    const focus = vi.spyOn(HTMLElement.prototype, "focus");
    renderWithClient(<App />);
    await screen.findByRole("button", { name: "Open report" });

    await userEvent.type(
      screen.getByRole("textbox", { name: "Message Grabbit" }),
      "Shorter, co-investors first{Enter}",
    );
    await screen.findByText(/Rewritten for you/);
    const panel = document.getElementById("report-panel");
    const panelCalls = focus.mock.contexts
      .map((ctx, i) => [ctx, focus.mock.calls[i][0]] as const)
      .filter(([ctx]) => ctx === panel);
    expect(panelCalls.at(-1)?.[1]).toEqual({ focusVisible: false });
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
