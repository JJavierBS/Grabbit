import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { setTransport } from "../../api/client";
import { renderWithClient } from "../../test/renderApp";
import { ChatPanel } from "./ChatPanel";

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });

/** A backend whose chat turn stays open until `finish` is called, like a long live turn. */
function slowBackend(outcome: "ok" | "fail") {
  let finish: () => void = () => {};
  const done = new Promise<void>((resolve) => {
    finish = resolve;
  });
  setTransport(async (request) => {
    const key = `${request.method} ${new URL(request.url).pathname}`;
    if (key === "GET /api/chat") return json([]);
    if (key === "POST /api/chat") {
      await done;
      return outcome === "ok"
        ? json({ messages: [] })
        : json({ error: { code: "llm_error", message: "Gemini timed out" } }, 502);
    }
    return json({ error: { code: "not_found", message: key } }, 404);
  });
  return { finish: () => finish() };
}

describe("ChatPanel while the agent works", () => {
  it("empties the composer at once and shows the working line last", async () => {
    const turn = slowBackend("ok");
    renderWithClient(<ChatPanel footer={<p>Report card</p>} />);
    const box = await screen.findByRole("textbox", { name: "Message Grabbit" });

    await userEvent.type(box, "AI at pre-seed{Enter}");
    expect(box).toHaveValue("");
    const working = await screen.findByText(/walking the Slush attendees in Cala/);
    const log = screen.getByRole("log");
    const items = [...log.querySelectorAll("p")].map((p) => p.textContent ?? "");
    expect(items.indexOf("Report card")).toBeLessThan(
      items.findIndex((t) => t.includes("walking the Slush attendees")),
    );
    expect(working).toBeInTheDocument();

    turn.finish();
    await waitFor(() => expect(screen.queryByText(/walking the Slush/)).not.toBeInTheDocument());
    expect(box).toHaveValue("");
  });

  it("puts the message back in the composer when it is not sent", async () => {
    const turn = slowBackend("fail");
    renderWithClient(<ChatPanel />);
    const box = await screen.findByRole("textbox", { name: "Message Grabbit" });

    await userEvent.type(box, "AI at pre-seed{Enter}");
    expect(box).toHaveValue("");
    turn.finish();

    expect(await screen.findByText(/Your message was not sent/)).toBeInTheDocument();
    expect(box).toHaveValue("AI at pre-seed");
  });
});
