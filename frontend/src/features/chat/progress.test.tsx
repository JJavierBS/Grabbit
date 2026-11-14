import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { setTransport } from "../../api/client";
import { useEvents } from "../../api/hooks/useEvents";
import type { ChatMessage, TurnProgress } from "../../api/types";
import { installTestStreams } from "../../test/fakeEvents";
import { renderWithClient } from "../../test/renderApp";
import { ChatPanel } from "./ChatPanel";
import { WorkingLine, workingText } from "./WorkingLine";

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });

function ChatWithEvents() {
  useEvents(() => undefined);
  return <ChatPanel />;
}

/** Chat turns that stay open until `finish`, plus the fake event stream. */
function heldTurns() {
  const streams = installTestStreams();
  let finish: () => void = () => {};
  setTransport(async (request) => {
    const key = `${request.method} ${new URL(request.url).pathname}`;
    if (key === "GET /api/chat") return json([]);
    if (key === "POST /api/chat") {
      await new Promise<void>((resolve) => {
        finish = resolve;
      });
      const reply: ChatMessage = {
        id: `a-${Math.random()}`,
        role: "agent",
        text: "Done.",
        report_id: null,
        ui: null,
        graph: null,
        walk: null,
        created_at: "2026-11-14T09:00:00Z",
        profile_changes: [],
      };
      return json(reply);
    }
    return json({ error: { code: "x", message: key } }, 404);
  });
  return { streams, finish: () => finish() };
}

describe("turn progress", () => {
  it("shows the phase the backend reports instead of the generic line", () => {
    render(<WorkingLine hasReport={false} phase="Rewriting your report…" />);
    expect(screen.getByRole("status")).toHaveTextContent("Rewriting your report…");
    expect(screen.getByRole("status")).not.toHaveTextContent(workingText(false));
  });

  it("follows progress events during a turn and starts the next turn fresh", async () => {
    const backend = heldTurns();
    renderWithClient(<ChatWithEvents />);
    const box = await screen.findByRole("textbox", { name: "Message Grabbit" });
    act(() => backend.streams[0].open());

    await userEvent.type(box, "AI at seed{Enter}");
    expect(await screen.findByText(workingText(false))).toBeInTheDocument();

    const phase: TurnProgress = {
      phase: "llm",
      label: "Reading your message…",
      done: null,
      total: null,
    };
    act(() => backend.streams[0].push("progress", phase));
    expect(await screen.findByText("Reading your message…")).toBeInTheDocument();

    backend.finish();
    await waitFor(() =>
      expect(screen.queryByText("Reading your message…")).not.toBeInTheDocument(),
    );

    await userEvent.type(box, "And Helsinki?{Enter}");
    expect(await screen.findByText(workingText(false))).toBeInTheDocument();
    expect(screen.queryByText("Reading your message…")).not.toBeInTheDocument();
    backend.finish();
    await waitFor(() => expect(screen.queryByText(workingText(false))).not.toBeInTheDocument());
  });
});
