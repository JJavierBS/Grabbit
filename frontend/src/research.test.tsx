import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Grabbit } from "./App";
import { setTransport } from "./api/client";
import type { ChatMessage } from "./api/types";
import { installTestStreams } from "./test/fakeEvents";
import { renderWithClient } from "./test/renderApp";

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });

/** A backend that keeps each workspace's chat apart, as the real one does (#85). */
function backend() {
  const streams = installTestStreams();
  const chats = new Map<string, ChatMessage[]>();
  const seen: string[] = [];
  setTransport(async (request) => {
    const ws = request.headers.get("X-Workspace") ?? "default";
    seen.push(ws);
    const key = `${request.method} ${new URL(request.url).pathname}`;
    const chat = chats.get(ws) ?? [];
    chats.set(ws, chat);
    if (key === "GET /api/chat") return json(chat);
    if (key === "POST /api/chat") {
      const { text } = await request.json();
      const at = "2026-11-14T09:00:00Z";
      const base = {
        report_id: null,
        ui: null,
        graph: null,
        walk: null,
        sources: [],
        questions: [],
      };
      chat.push({
        ...base,
        id: `u${chat.length}`,
        role: "user",
        text,
        created_at: at,
        profile_changes: [],
      });
      const reply = {
        ...base,
        id: `a${chat.length}`,
        role: "agent" as const,
        text: `Noted: ${text}.`,
        created_at: at,
        profile_changes: [],
      };
      chat.push(reply);
      return json(reply);
    }
    if (key === "GET /api/reports") return json([]);
    return json({ error: { code: "not_found", message: key } }, 404);
  });
  return { streams, seen };
}

const WELCOME = "Tell me what you look for at Slush 2026.";

beforeEach(() => localStorage.clear());

describe("new research (#145)", () => {
  it("starts a fresh research and goes back to the earlier one with its chat", async () => {
    const api = backend();
    renderWithClient(<Grabbit />);
    const box = await screen.findByRole("textbox", { name: "Message Grabbit" });
    await userEvent.type(box, "AI at seed{Enter}");
    expect(await screen.findByText("Noted: AI at seed.")).toBeInTheDocument();
    const first = api.seen.at(-1);

    await userEvent.click(screen.getAllByRole("button", { name: "New research" })[0]);
    expect(await screen.findByText(WELCOME)).toBeInTheDocument();
    expect(screen.queryByText("Noted: AI at seed.")).toBeNull();
    await waitFor(() => expect(api.seen.at(-1)).not.toBe(first));
    // The event stream follows the research too.
    expect(api.streams.at(-1)?.url).toBe("/api/events");
    expect(api.streams.filter((s) => !s.closed)).toHaveLength(1);

    const list = screen.getByRole("navigation", { name: "Research" });
    const items = within(list).getAllByRole("button");
    expect(items.map((b) => b.textContent)).toEqual([
      expect.stringContaining("New research"),
      expect.stringContaining("AI at seed"),
    ]);
    expect(items[0]).toHaveAttribute("aria-current", "true");

    await userEvent.click(items[1]);
    expect(await screen.findByText("Noted: AI at seed.")).toBeInTheDocument();
    expect(screen.queryByText(WELCOME)).toBeNull();
    expect(api.seen.at(-1)).toBe(first);
  });

  it("does not pile up empty researches", async () => {
    backend();
    renderWithClient(<Grabbit />);
    await screen.findByText(WELCOME);
    const [newResearch] = screen.getAllByRole("button", { name: "New research" });
    await userEvent.click(newResearch);
    await userEvent.click(newResearch);
    expect(screen.queryByRole("navigation", { name: "Research" })).toBeNull();
    expect(JSON.parse(localStorage.getItem("grabbit.researches") ?? "[]")).toHaveLength(1);
  });
});
