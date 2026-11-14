import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { AgentQuestion, ChatMessage } from "../../api/types";
import { mockApi, renderWithClient } from "../../test/renderApp";
import { AgentQuestions, composeAnswer } from "./AgentQuestions";
import { ChatPanel } from "./ChatPanel";

const questions: AgentQuestion[] = [
  {
    key: "recency",
    text: "36 raised in the last 12 months and 36 earlier. Startups that just raised, or ones that may raise soon?",
    options: [
      { label: "Just raised", answer: "Show me startups that raised in the last 12 months." },
      { label: "May raise soon", answer: "Show me startups that may raise soon." },
    ],
  },
  {
    key: "team",
    text: "Teams range from 9 to 500 people. Prefer small teams?",
    options: [
      { label: "Small teams, up to 20", answer: "Prefer small teams, up to 20 people." },
      { label: "Any size", answer: "Team size does not matter to me." },
    ],
  },
];

describe("clickable first questions (#153)", () => {
  it("joins the chosen answers in the order they were asked", () => {
    expect(composeAnswer(questions, { team: "B.", recency: "A." })).toBe("A. B.");
    expect(composeAnswer(questions, {})).toBe("");
  });

  it("is a form of radio groups, sent with one click, unanswered ones skipped", async () => {
    const sent: string[] = [];
    render(<AgentQuestions questions={questions} onAnswer={(t) => sent.push(t)} />);
    const send = screen.getByRole("button", { name: "Send answers" });
    expect(send).toBeDisabled();

    const team = screen.getByRole("group", { name: questions[1].text });
    await userEvent.click(within(team).getByRole("radio", { name: "Small teams, up to 20" }));
    await userEvent.click(within(team).getByRole("radio", { name: "Any size" }));
    expect(within(team).getByRole("radio", { name: "Any size" })).toBeChecked();
    expect(within(team).getByRole("radio", { name: "Small teams, up to 20" })).not.toBeChecked();

    await userEvent.click(send);
    expect(sent).toEqual(["Team size does not matter to me."]);
  });

  it("waits while a turn runs", async () => {
    const sent: string[] = [];
    render(<AgentQuestions questions={questions} onAnswer={(t) => sent.push(t)} busy />);
    await userEvent.click(screen.getByRole("radio", { name: "Just raised" }));
    expect(screen.getByRole("button", { name: "Send answers" })).toBeDisabled();
  });

  it("answers through the chat, then stays as a read-only record", async () => {
    const agent: ChatMessage = {
      id: "a1",
      role: "agent",
      text: "I focused on AI at seed.",
      created_at: "2026-11-14T09:00:00Z",
      profile_changes: [],
      report_id: null,
      ui: null,
      graph: null,
      walk: null,
      sources: [],
      questions,
    };
    const chat: ChatMessage[] = [agent];
    const api = mockApi({
      "GET /api/chat": () => chat,
      "POST /api/chat": (body) => {
        const { text } = body as { text: string };
        chat.push({ ...agent, id: "u2", role: "user", text, questions: [] });
        const reply = { ...agent, id: "a3", text: "Noted.", questions: [] };
        chat.push(reply);
        return reply;
      },
    });
    renderWithClient(<ChatPanel />);
    await userEvent.click(await screen.findByRole("radio", { name: "May raise soon" }));
    await userEvent.click(screen.getByRole("radio", { name: "Small teams, up to 20" }));
    await userEvent.click(screen.getByRole("button", { name: "Send answers" }));

    await waitFor(() => expect(api.some((c) => c.key === "POST /api/chat")).toBe(true));
    expect(api.find((c) => c.key === "POST /api/chat")?.body).toEqual({
      text: "Show me startups that may raise soon. Prefer small teams, up to 20 people.",
    });
    // The conversation moved on: the questions are now what was asked, not a form.
    await waitFor(() => expect(screen.queryByRole("radio")).toBeNull());
    expect(screen.getByRole("list", { name: "Questions Grabbit asked" })).toHaveTextContent(
      "Prefer small teams?",
    );
  });
});
