import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ChatMessage } from "../../api/types";
import { reportV1 } from "../../dev/fixtures";
import { mockApi, renderWithClient } from "../../test/renderApp";
import {
  ChatPanel,
  CORRECTIONS,
  PLACEHOLDER_FIRST,
  PLACEHOLDER_REPORT,
  THESIS_EXAMPLES,
} from "./ChatPanel";

const noReport = {
  status: 404,
  body: { error: { code: "no_report", message: "No report has been generated yet." } },
};

const hello: ChatMessage = {
  id: "a1",
  role: "agent",
  text: "Which stage?",
  report_id: null,
  ui: null,
  graph: null,
  created_at: "2026-11-14T09:00:00Z",
  profile_changes: [],
};

describe("first run", () => {
  it("invites a thesis with examples that send themselves", async () => {
    const calls = mockApi({
      "GET /api/chat": () => [],
      "GET /api/reports/latest": noReport,
      "POST /api/chat": () => hello,
    });
    renderWithClient(<ChatPanel />);
    const log = screen.getByRole("log");
    expect(
      await within(log).findByText("Tell me what you look for at Slush 2026."),
    ).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Message Grabbit" })).toHaveAttribute(
      "placeholder",
      PLACEHOLDER_FIRST,
    );
    for (const example of THESIS_EXAMPLES) {
      expect(screen.getByRole("button", { name: example })).toBeInTheDocument();
    }
    for (const correction of CORRECTIONS) {
      expect(screen.queryByRole("button", { name: correction })).not.toBeInTheDocument();
    }

    await userEvent.click(screen.getByRole("button", { name: THESIS_EXAMPLES[0] }));
    expect(calls.find((c) => c.key === "POST /api/chat")?.body).toEqual({
      text: THESIS_EXAMPLES[0],
    });
  });

  it("shows no chips while the agent is still asking, before any report", async () => {
    mockApi({ "GET /api/chat": () => [hello], "GET /api/reports/latest": noReport });
    renderWithClient(<ChatPanel />);
    await screen.findByText("Which stage?");
    expect(screen.queryByRole("button", { name: THESIS_EXAMPLES[0] })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: CORRECTIONS[0] })).not.toBeInTheDocument();
    expect(screen.queryByText("Tell me what you look for at Slush 2026.")).not.toBeInTheDocument();
  });

  it("offers corrections and the correction placeholder once a report exists", async () => {
    mockApi({ "GET /api/chat": () => [hello], "GET /api/reports/latest": () => reportV1 });
    renderWithClient(<ChatPanel />);
    expect(await screen.findByRole("button", { name: CORRECTIONS[0] })).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: THESIS_EXAMPLES[0] })).not.toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Message Grabbit" })).toHaveAttribute(
      "placeholder",
      PLACEHOLDER_REPORT,
    );
  });
});
