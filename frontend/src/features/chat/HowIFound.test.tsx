import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ChatMessage } from "../../api/types";
import { exploredAnswerUi, exploredAurora, exploredAuroraWalk } from "../../dev/fixtures";
import { mockApi, renderWithClient } from "../../test/renderApp";
import { ChatPanel } from "./ChatPanel";
import { HowIFound, summaryText } from "./HowIFound";

describe("How I found this", () => {
  it("sums the walk up in one plain line", () => {
    expect(summaryText(exploredAuroraWalk)).toBe(
      `Checked ${exploredAurora.nodes.length} companies, people and rounds in Cala in 9 s`,
    );
    expect(summaryText({ ...exploredAuroraWalk, checked: 1, seconds: 0.4 })).toBe(
      "Checked 1 company, person or round in Cala in under a second",
    );
  });

  it("stays folded until the reader opens it, then lists every step", async () => {
    render(<HowIFound walk={exploredAuroraWalk} />);
    const steps = screen.getByRole("list", { name: "How I found this, step by step" });
    expect(steps).not.toBeVisible();
    await userEvent.click(screen.getByText("How I found this"));
    expect(steps).toBeVisible();
    expect(steps).toHaveTextContent("Searching Cala for “Aurora Ventures” → found Aurora Ventures");
    expect(screen.getAllByRole("listitem")).toHaveLength(exploredAuroraWalk.steps.length);
  });

  it("is kept on a stored answer that walked Cala, and absent on one that did not", async () => {
    const answer = (id: string, walk: ChatMessage["walk"]): ChatMessage => ({
      id,
      role: "agent",
      text: "Aurora led both.",
      created_at: "2026-11-14T09:00:00Z",
      profile_changes: [],
      report_id: null,
      ui: exploredAnswerUi,
      graph: exploredAurora,
      walk,
      sources: [],
      questions: [],
    });
    mockApi({ "GET /api/chat": () => [answer("a1", exploredAuroraWalk), answer("a2", null)] });
    renderWithClient(<ChatPanel />);
    expect(await screen.findAllByText("How I found this")).toHaveLength(1);
  });
});
