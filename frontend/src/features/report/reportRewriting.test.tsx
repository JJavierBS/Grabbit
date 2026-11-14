import { act, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { App } from "../../App";
import type { ChatMessage, Profile } from "../../api/types";
import { historyV2, profileV2, reportV1, reportV2 } from "../../dev/fixtures";
import { mockApi, renderWithClient } from "../../test/renderApp";
import { isRewriting, REWRITE_WAIT_MS, REWRITING_TEXT } from "./useReportRewriting";

const now = Date.parse("2026-11-14T10:00:00Z");
const at = (msAgo: number) => new Date(now - msAgo).toISOString();

describe("isRewriting", () => {
  it("is on while the profile is newer than the report, for at most the wait", () => {
    const report = { profile_version: 2 };
    expect(isRewriting({ version: 3, updated_at: at(5_000) }, report, now)).toBe(true);
    expect(isRewriting({ version: 3, updated_at: at(REWRITE_WAIT_MS + 1) }, report, now)).toBe(
      false,
    );
  });

  it("is off when the report already matches, or when there is nothing to compare", () => {
    expect(isRewriting({ version: 2, updated_at: at(1_000) }, { profile_version: 2 }, now)).toBe(
      false,
    );
    expect(isRewriting(undefined, { profile_version: 2 }, now)).toBe(false);
    expect(isRewriting({ version: 3, updated_at: at(1_000) }, null, now)).toBe(false);
  });
});

const msg = (id: string, role: ChatMessage["role"], text: string, report_id: string | null) =>
  ({
    id,
    role,
    text,
    report_id,
    ui: null,
    graph: null,
    walk: null,
    sources: [],
    questions: [],
    created_at: "2026-11-14T09:00:00Z",
    profile_changes: [],
  }) satisfies ChatMessage;

describe("report rewriting in the app", () => {
  it("says the report is being rewritten, under the turn that asked, until it lands", async () => {
    // The correction saved profile v3 and scheduled rep-2; the latest report is still rep-1.
    const profileV3: Profile = { ...profileV2, version: 3, updated_at: new Date().toISOString() };
    let latest = reportV1;
    const calls = mockApi({
      "GET /api/profile": () => profileV3,
      "GET /api/profile/history": () => historyV2,
      "GET /api/alerts": () => [],
      "GET /api/reports": () => [],
      "GET /api/reports/latest": () => latest,
      "GET /api/chat": () => [
        msg("a1", "agent", "Here is your first report.", reportV1.id),
        msg("u2", "user", "Shorter, co-investors first", null),
        msg("a2", "agent", "Understood.", reportV2.id),
      ],
    });
    renderWithClient(<App />);

    const outline = await screen.findByRole("article", { name: "Slush 2026 prep report outline" });
    expect(within(outline).getByText(REWRITING_TEXT)).toBeInTheDocument();
    expect(outline).toHaveAttribute("aria-busy", "true");
    const turn = screen.getByText("Understood.").closest("article") as Element;
    expect(turn.compareDocumentPosition(outline) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();

    await userEvent.click(within(outline).getByRole("button", { name: "Open report" }));
    const panel = document.getElementById("report-panel") as HTMLElement;
    expect(within(panel).getByText(REWRITING_TEXT)).toBeInTheDocument();

    // The rebuilt report lands: the backend sends a `report` event and the app refetches.
    latest = reportV2;
    act(() => {
      calls.streams[0].open();
      calls.streams[0].push("report", { id: reportV2.id });
    });
    await waitFor(() => expect(screen.queryByText(REWRITING_TEXT)).toBeNull());
  });
});
