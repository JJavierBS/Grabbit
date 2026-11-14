import { act, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { setTransport } from "../../api/client";
import { useEvents } from "../../api/hooks/useEvents";
import type { ChatMessage, WalkStep, WalkTrace } from "../../api/types";
import { exploredAurora } from "../../dev/fixtures";
import { cssFile, declarations } from "../../test/css";
import { installTestStreams } from "../../test/fakeEvents";
import { renderWithClient } from "../../test/renderApp";
import { ChatPanel } from "./ChatPanel";
import { budgetText, checkedText, LiveWalk, VISIBLE_STEPS } from "./LiveWalk";

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });

const step = (id: number, over: Partial<WalkStep> = {}): WalkStep => ({
  id,
  kind: "expand",
  text: `Expanding entity ${id}`,
  result: "+2 entities, +2 links",
  done: true,
  ...over,
});

const trace = (over: Partial<WalkTrace> = {}): WalkTrace => ({
  turn: "t1",
  round: 1,
  max_rounds: 6,
  nodes: 0,
  max_nodes: 30,
  steps: [],
  graph: null,
  root_id: null,
  answer: null,
  streaming: false,
  done: false,
  ...over,
});

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

describe("LiveWalk", () => {
  it("says how far the walk is in words anyone reads", () => {
    expect(budgetText(trace({ round: 2, nodes: 14 }))).toBe(
      "Step 2 of up to 6 · 14 companies, people and rounds checked",
    );
    expect(budgetText(trace({ round: 0 }))).toBe("nothing checked yet");
    expect(checkedText(1)).toBe("1 company, person or round checked");
    for (const text of [budgetText(trace({ round: 3, nodes: 9 })), checkedText(9)]) {
      expect(text).not.toMatch(/entit|node|edge|link/i);
    }
  });

  it("explains the walk in one line and draws its progress", () => {
    const { container } = renderWithClient(
      <LiveWalk trace={trace({ round: 3, steps: [step(0)] })} />,
    );
    expect(screen.getByText("Reading Cala's map of who funds whom")).toBeInTheDocument();
    const bar = container.querySelector("header [aria-hidden='true'] > span") as HTMLElement;
    expect(bar.style.width).toBe("50%");
  });

  it("shows the latest steps, folds the older ones and marks the model's reasoning", () => {
    const steps = [
      ...Array.from({ length: VISIBLE_STEPS + 2 }, (_, i) => step(i)),
      step(VISIBLE_STEPS + 2, { kind: "thought", text: "The fund is the lead.", result: null }),
      step(VISIBLE_STEPS + 3, { kind: "search", text: "Searching Cala for “A”", done: false }),
    ];
    renderWithClient(<LiveWalk trace={trace({ steps })} />);
    const list = screen.getByRole("list", { name: "Steps" });
    expect(within(list).getAllByRole("listitem")).toHaveLength(VISIBLE_STEPS + 1);
    expect(list).toHaveTextContent("4 earlier steps");
    expect(list).toHaveTextContent("Model's reasoning: The fund is the lead.");
    expect(list).toHaveTextContent("Searching Cala for “A”…");
    expect(list).not.toHaveTextContent("Expanding entity 0");
  });

  it("draws the graph growing from its root and the answer as it streams", () => {
    const ui = 'root = Answer([t])\nt = Text("Aurora led both rounds.")';
    renderWithClient(
      <LiveWalk
        trace={trace({
          steps: [step(0)],
          graph: exploredAurora,
          root_id: "i-aurora",
          nodes: exploredAurora.nodes.length,
          answer: ui,
          streaming: true,
        })}
      />,
    );
    const figure = screen.getByRole("figure");
    expect(figure).toHaveAttribute("data-live");
    expect(figure).toHaveTextContent("Growing as Grabbit walks Cala's entity graph");
    expect(screen.getByText("Aurora led both rounds.")).toBeInTheDocument();
  });

  it("fades new entities in only on the live graph, and not with reduced motion", () => {
    const css = cssFile("features/chat/openui/ExploredGraphView.module.css");
    expect(declarations(css, ".figure[data-live] .edge").animation).toContain(
      "var(--duration-slow)",
    );
    // --duration-slow is 0ms under reduced motion (styles/tokens.css).
    expect(cssFile("styles/tokens.css")).toMatch(/--duration-slow: 0ms/);
  });

  it("follows trace events during a turn and leaves when the reply arrives", async () => {
    const backend = heldTurns();
    renderWithClient(<ChatWithEvents />);
    const box = await screen.findByRole("textbox", { name: "Message Grabbit" });
    act(() => backend.streams[0].open());

    await userEvent.type(box, "Who backs Aurora?{Enter}");
    act(() =>
      backend.streams[0].push(
        "trace",
        trace({ steps: [step(0, { kind: "search", text: "Searching Cala for “Aurora”" })] }),
      ),
    );
    const walk = await screen.findByRole("region", { name: "Grabbit walking Cala's graph" });
    expect(walk).toHaveTextContent("Searching Cala for “Aurora”");

    act(() =>
      backend.streams[0].push(
        "trace",
        trace({
          round: 2,
          steps: [step(0), step(1)],
          graph: exploredAurora,
          root_id: "i-aurora",
          nodes: exploredAurora.nodes.length,
        }),
      ),
    );
    const grown = screen.getByRole("region", { name: "Grabbit walking Cala's graph" });
    await waitFor(() =>
      expect(grown).toHaveTextContent(
        `Step 2 of up to 6 · ${exploredAurora.nodes.length} companies, people and rounds`,
      ),
    );
    expect(within(grown).getByRole("figure")).toBeInTheDocument();

    backend.finish();
    await waitFor(() =>
      expect(
        screen.queryByRole("region", { name: "Grabbit walking Cala's graph" }),
      ).not.toBeInTheDocument(),
    );

    // The next turn starts without the last walk.
    await userEvent.type(box, "And Helsinki?{Enter}");
    expect(screen.queryByRole("region", { name: "Grabbit walking Cala's graph" })).toBeNull();
    backend.finish();
  });
});
