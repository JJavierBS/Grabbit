import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { App } from "./App";
import { setTransport } from "./api/client";
import type { Alert, ChatMessage } from "./api/types";
import { historyV2, profileV2, reportV1 } from "./dev/fixtures";
import { ChatPanel } from "./features/chat/ChatPanel";
import { mockApi, renderWithClient } from "./test/renderApp";

const msg = (
  id: string,
  role: ChatMessage["role"],
  text: string,
  report_id: string | null = null,
) =>
  ({
    id,
    role,
    text,
    report_id,
    ui: null,
    graph: null,
    created_at: "2026-11-14T09:00:00Z",
    profile_changes: [],
  }) satisfies ChatMessage;

const base = {
  "GET /api/profile": () => profileV2,
  "GET /api/profile/history": () => historyV2,
  "GET /api/alerts": () => [],
  "GET /api/reports": () => [],
  "GET /api/reports/latest": () => reportV1,
};

const precedes = (a: Element, b: Element) =>
  Boolean(a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING);

const article = (text: RegExp) => screen.getByText(text).closest("article") as Element;

describe("chat reading order", () => {
  it("puts the report outline after the turn that wrote it, and later replies below it", async () => {
    mockApi({
      ...base,
      "GET /api/chat": () => [
        msg("u1", "user", "AI at pre-seed"),
        msg("a1", "agent", "Here is your first report.", reportV1.id),
        msg("u2", "user", "Who is in Helsinki?"),
        msg("a2", "agent", "Two of them are in Helsinki."),
      ],
    });
    renderWithClient(<App />);
    const outline = await screen.findByRole("article", { name: "Slush 2026 prep report outline" });
    expect(precedes(article(/Here is your first report/), outline)).toBe(true);
    expect(precedes(outline, article(/Two of them are in Helsinki/))).toBe(true);
  });

  it("puts a report no turn wrote after the conversation", async () => {
    mockApi({
      ...base,
      "GET /api/chat": () => [msg("u1", "user", "Hi"), msg("a1", "agent", "Hello there.")],
    });
    renderWithClient(<App />);
    const outline = await screen.findByRole("article", { name: "Slush 2026 prep report outline" });
    expect(precedes(article(/Hello there/), outline)).toBe(true);
  });

  it("keeps an opened alert where it was opened when the chat moves on", async () => {
    let chat = [msg("a1", "agent", "Watching your shortlist.")];
    const calls = mockApi({
      ...base,
      "GET /api/chat": () => chat,
      "POST /api/chat": () => {
        chat = [...chat, msg("u2", "user", "Tell me more"), msg("a2", "agent", "GREÏ raised.")];
        return chat.at(-1);
      },
    });
    renderWithClient(<App />);
    await screen.findByText("Watching your shortlist.");
    const alert: Alert = {
      id: "al-7",
      created_at: "2026-11-14T10:00:00Z",
      entity_id: "c-grei",
      entity_name: "GREÏ",
      kind: "new_round",
      title: "GREÏ announced a Seed",
      why_it_matters: "Led by Y Combinator.",
      importance: 0.9,
      facts: [],
      simulated: true,
    };
    calls.streams[0].open();
    calls.streams[0].push("alert", alert);
    await userEvent.click(screen.getByRole("button", { name: "Open in chat" }));

    await userEvent.type(
      screen.getByRole("textbox", { name: "Message Grabbit" }),
      "Tell me more{Enter}",
    );
    const card = screen.getByRole("article", { name: "GREÏ announced a Seed" });
    const reply = await screen.findByText("GREÏ raised.");
    expect(precedes(card, reply)).toBe(true);
  });

  it("shows a placeholder for the report card while the report loads", async () => {
    const never = new Promise<Response>(() => {});
    setTransport(async (request) => {
      const path = new URL(request.url).pathname;
      if (path === "/api/reports/latest") return never;
      if (path === "/api/chat") return new Response("[]");
      return new Response(JSON.stringify({ error: { code: "x", message: path } }), { status: 404 });
    });
    renderWithClient(<App />);
    expect(await screen.findByText("Loading the report")).toBeInTheDocument();
  });
});

describe("following the conversation", () => {
  /** A chat whose next turn adds a user message and an agent reply once `answer` is called. */
  function turnBackend() {
    let chat: ChatMessage[] = [msg("a1", "agent", "Earlier reply.")];
    let answer: () => void = () => {};
    const answered = new Promise<void>((resolve) => {
      answer = resolve;
    });
    const json = (body: unknown) => new Response(JSON.stringify(body));
    setTransport(async (request) => {
      const key = `${request.method} ${new URL(request.url).pathname}`;
      if (key === "GET /api/chat") return json(chat);
      if (key === "POST /api/chat") {
        await answered;
        chat = [...chat, msg("u2", "user", "And Helsinki?"), msg("a2", "agent", "Two are there.")];
        return json(chat.at(-1));
      }
      return new Response(JSON.stringify({ error: { code: "x", message: key } }), { status: 404 });
    });
    return { answer: () => answer() };
  }

  it("animates only the messages that arrive during the visit", async () => {
    const turn = turnBackend();
    renderWithClient(<ChatPanel />);
    const earlier = (await screen.findByText("Earlier reply.")).closest("article");
    expect(earlier).not.toHaveAttribute("data-enter");

    await userEvent.type(
      screen.getByRole("textbox", { name: "Message Grabbit" }),
      "And Helsinki?{Enter}",
    );
    turn.answer();
    const reply = (await screen.findByText("Two are there.")).closest("article");
    expect(reply).toHaveAttribute("data-enter");
    expect(earlier).not.toHaveAttribute("data-enter");
  });

  it("offers Jump to latest when a reply lands while the reader is scrolled up", async () => {
    const turn = turnBackend();
    renderWithClient(<ChatPanel />);
    await screen.findByText("Earlier reply.");
    const log = screen.getByRole("log");
    const scrollTo = vi.fn();
    Object.assign(log, { scrollTo });
    Object.defineProperties(log, {
      scrollHeight: { configurable: true, value: 2000 },
      clientHeight: { configurable: true, value: 500 },
      scrollTop: { configurable: true, writable: true, value: 0 },
    });

    // The reader sends, then scrolls up to reread while the agent answers.
    await userEvent.type(
      screen.getByRole("textbox", { name: "Message Grabbit" }),
      "And Helsinki?{Enter}",
    );
    await within(log).findByText("And Helsinki?");
    log.dispatchEvent(new Event("scroll"));
    turn.answer();
    await screen.findByText("Two are there.");

    const jump = await screen.findByRole("button", { name: "Jump to latest" });
    scrollTo.mockClear();
    await userEvent.click(jump);
    expect(scrollTo).toHaveBeenCalledWith(expect.objectContaining({ top: 2000 }));
    await waitFor(() =>
      expect(screen.queryByRole("button", { name: "Jump to latest" })).not.toBeInTheDocument(),
    );
    expect(within(log).getByText("Two are there.")).toBeInTheDocument();
  });
});
