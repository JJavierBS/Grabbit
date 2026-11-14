import { act, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Grabbit } from "./App";
import { setTransport } from "./api/client";
import type { ChatMessage } from "./api/types";
import { installTestStreams } from "./test/fakeEvents";
import { renderWithClient } from "./test/renderApp";

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });

const message = (id: string, role: ChatMessage["role"], text: string): ChatMessage => ({
  id,
  role,
  text,
  report_id: null,
  ui: null,
  graph: null,
  walk: null,
  sources: [],
  questions: [],
  created_at: "2026-11-14T09:00:00Z",
  profile_changes: [],
});

/** A backend that keeps each research's chat apart, as the real one does. */
function backend(onTurn?: () => void) {
  installTestStreams();
  const chats = new Map<string, ChatMessage[]>();
  setTransport(async (request) => {
    const ws = request.headers.get("X-Workspace") ?? "default";
    const key = `${request.method} ${new URL(request.url).pathname}`;
    const chat = chats.get(ws) ?? [];
    chats.set(ws, chat);
    if (key === "GET /api/chat") return json(chat);
    if (key === "POST /api/chat") {
      const { text } = await request.json();
      onTurn?.();
      chat.push(message(`u${chat.length}`, "user", text));
      const reply = message(`a${chat.length}`, "agent", `Noted: ${text}.`);
      chat.push(reply);
      return json(reply);
    }
    if (key === "GET /api/reports") return json([]);
    return json({ error: { code: "not_found", message: key } }, 404);
  });
}

const box = () => screen.getByRole("textbox", { name: "Message Grabbit" });

describe("the message box keeps focus (#188)", () => {
  it("takes focus when the chat opens and on a new research", async () => {
    backend();
    renderWithClient(<Grabbit />);
    await screen.findByRole("textbox", { name: "Message Grabbit" });
    expect(box()).toHaveFocus();

    await userEvent.type(box(), "AI at seed{Enter}");
    expect(await screen.findByText("Noted: AI at seed.")).toBeInTheDocument();
    await userEvent.click(screen.getAllByRole("button", { name: "New research" })[0]);
    await screen.findByText("Tell me what you look for at Slush 2026.");
    expect(box()).toHaveFocus();
  });

  it("starts a new research with Ctrl+Shift+O", async () => {
    backend();
    renderWithClient(<Grabbit />);
    await userEvent.type(
      await screen.findByRole("textbox", { name: "Message Grabbit" }),
      "AI{Enter}",
    );
    expect(await screen.findByText("Noted: AI.")).toBeInTheDocument();

    await userEvent.keyboard("{Control>}{Shift>}O{/Shift}{/Control}");
    await screen.findByText("Tell me what you look for at Slush 2026.");
    expect(box()).toHaveFocus();
  });

  it("keeps each research's draft and focuses it on switching back", async () => {
    backend();
    renderWithClient(<Grabbit />);
    await userEvent.type(
      await screen.findByRole("textbox", { name: "Message Grabbit" }),
      "AI{Enter}",
    );
    expect(await screen.findByText("Noted: AI.")).toBeInTheDocument();
    await userEvent.type(box(), "and climate");

    await userEvent.click(screen.getAllByRole("button", { name: "New research" })[0]);
    await screen.findByText("Tell me what you look for at Slush 2026.");
    expect(box()).toHaveValue("");

    const list = screen.getByRole("navigation", { name: "Research" });
    await userEvent.click(within(list).getByRole("button", { name: /AI/ }));
    expect(await screen.findByText("Noted: AI.")).toBeInTheDocument();
    expect(box()).toHaveValue("and climate");
    expect(box()).toHaveFocus();

    await userEvent.keyboard("{Enter}");
    expect(await screen.findByText("Noted: and climate.")).toBeInTheDocument();
    expect(
      localStorage.getItem(`grabbit.draft:${localStorage.getItem("grabbit.workspace")}`),
    ).toBeNull();
  });

  it("comes back to the box after a suggestion is sent", async () => {
    backend();
    renderWithClient(<Grabbit />);
    await userEvent.click(
      await screen.findByRole("button", { name: "Nordic climate tech at seed" }),
    );
    expect(await screen.findByText("Noted: Nordic climate tech at seed.")).toBeInTheDocument();
    expect(box()).toHaveFocus();
  });

  it("types a stray character into the box", async () => {
    backend();
    renderWithClient(<Grabbit />);
    await screen.findByRole("textbox", { name: "Message Grabbit" });
    act(() => box().blur());
    expect(box()).not.toHaveFocus();

    await userEvent.keyboard("A");
    expect(box()).toHaveFocus();
  });

  it("gives the box back when the reply arrives", async () => {
    // The reader clicked away while the agent worked.
    backend(() => act(() => (document.activeElement as HTMLElement | null)?.blur()));
    renderWithClient(<Grabbit />);
    await userEvent.type(
      await screen.findByRole("textbox", { name: "Message Grabbit" }),
      "AI{Enter}",
    );
    expect(await screen.findByText("Noted: AI.")).toBeInTheDocument();
    await waitFor(() => expect(box()).toHaveFocus());
  });
});
