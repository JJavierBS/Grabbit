import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { App } from "../../App";
import { historyV2, profileV2 } from "../../dev/fixtures";
import { mockApi, renderWithClient } from "../../test/renderApp";
import { DemoRoot } from "./DemoRoot";
import { createDemoApi } from "./demoApi";
import { DEMO_ANSWER, DEMO_STEPS, DEMO_THESIS } from "./steps";

const instant = { get: 0, post: 0, alert: 0 };
const SEEN = "grabbit.demo.seen:v1";
const RESEARCHES = "grabbit.researches";

const noReport = {
  status: 404,
  body: { error: { code: "no_report", message: "No report has been generated yet." } },
};

/** The visitor's own, empty research on the real API. */
const realApi = () =>
  mockApi({
    "GET /api/profile": () => profileV2,
    "GET /api/profile/history": () => historyV2,
    "GET /api/chat": () => [],
    "GET /api/alerts": () => [],
    "GET /api/reports": () => [],
    "GET /api/reports/latest": noReport,
  });

const renderWithDemo = () =>
  renderWithClient(
    <DemoRoot demo={<App />} timing={instant}>
      <App />
    </DemoRoot>,
  );

const card = async () => {
  const title = await screen.findByRole("heading", { level: 3 });
  const region = title.closest("section");
  if (!region) throw new Error("No coach card");
  return within(region);
};

async function step(title: string) {
  await screen.findByRole("heading", { level: 3, name: title });
}

beforeEach(() => {
  localStorage.clear();
  history.replaceState(null, "", "/");
});

describe("demo backend", () => {
  it("starts empty, with no report yet", async () => {
    const api = createDemoApi(instant);
    const chat = await api.transport(new Request("http://x/api/chat"));
    expect(await chat.json()).toEqual([]);
    const latest = await api.transport(new Request("http://x/api/reports/latest"));
    expect(latest.status).toBe(404);
    expect((await latest.json()).error.code).toBe("no_report");
  });

  it("gives each demo run its own state", async () => {
    const first = createDemoApi(instant);
    const second = createDemoApi(instant);
    await first.transport(
      new Request("http://x/api/chat", { method: "POST", body: JSON.stringify({ text: "AI" }) }),
    );
    const chat = await second.transport(new Request("http://x/api/chat"));
    expect(await chat.json()).toEqual([]);
  });

  it("asks a question after the thesis, then writes the report after the answer", async () => {
    const api = createDemoApi(instant);
    const post = (text: string) =>
      api
        .transport(
          new Request("http://x/api/chat", { method: "POST", body: JSON.stringify({ text }) }),
        )
        .then((r) => r.json());
    const asked = await post(DEMO_THESIS);
    expect(asked.questions).toHaveLength(1);
    expect(asked.report_id).toBeNull();
    const answered = await post(DEMO_ANSWER);
    expect(answered.report_id).toBe("rep-1");
  });
});

describe("guided demo", () => {
  it("invites a first-time visitor from the empty chat, with a marker until seen", async () => {
    realApi();
    renderWithDemo();
    const invite = await screen.findByRole("button", { name: /See how it works/ });
    expect(invite.querySelector("[class*=fresh]")).not.toBeNull();
    await userEvent.click(invite);
    await step(DEMO_STEPS[0].title);
    expect(localStorage.getItem(SEEN)).toBe("1");
  });

  it("drops the marker once the visitor sends their own first message", async () => {
    const calls = realApi();
    renderWithDemo();
    await userEvent.type(
      await screen.findByRole("textbox", { name: "Message Grabbit" }),
      "Climate at seed{Enter}",
    );
    await waitFor(() => expect(calls.some((c) => c.key === "POST /api/chat")).toBe(true));
    expect(localStorage.getItem(SEEN)).toBe("1");
  });

  it("walks the four steps on sample data with Show me, then hands back the real chat", async () => {
    const calls = realApi();
    renderWithDemo();
    await userEvent.click(await screen.findByRole("button", { name: /See how it works/ }));
    const before = calls.length;
    const researches = localStorage.getItem(RESEARCHES);

    // 1. Thesis: the agent comes back with a question.
    await step(DEMO_STEPS[0].title);
    await userEvent.click(screen.getByRole("button", { name: "Show me" }));
    expect(await screen.findByText(/Which investors do you trust/)).toBeInTheDocument();
    expect(await screen.findByText(DEMO_STEPS[0].outcome)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Next" }));

    // 2. Answer: the report lands and opens with its trust badges.
    await step(DEMO_STEPS[1].title);
    await userEvent.click(screen.getByRole("button", { name: "Show me" }));
    const panel = await screen.findByRole("region", { name: "Report" });
    expect(
      await within(panel).findByRole("heading", { name: "Slush 2026 prep report" }),
    ).toBeInTheDocument();
    expect(within(panel).getAllByText("Official filing").length).toBeGreaterThan(0);
    await userEvent.click(await screen.findByRole("button", { name: "Next" }));

    // 3. Correction: the report rewrites itself.
    await step(DEMO_STEPS[2].title);
    await userEvent.click(screen.getByRole("button", { name: "Show me" }));
    expect(await screen.findByText(/Rewritten for you/)).toBeInTheDocument();
    await userEvent.click(await screen.findByRole("button", { name: "Next" }));

    // 4. Confirmation: a simulated alert arrives, labelled as such.
    await step(DEMO_STEPS[3].title);
    await userEvent.click(screen.getByRole("button", { name: "Show me" }));
    const toasts = screen.getByRole("region", { name: "Notifications" });
    expect(await within(toasts).findByText("Simulated event")).toBeInTheDocument();
    await userEvent.click(await screen.findByRole("button", { name: "Finish" }));

    await step("That's the loop. Your turn.");
    // Nothing the demo did went to the real API or renamed the visitor's research.
    expect(calls.length).toBe(before);
    expect(localStorage.getItem(RESEARCHES)).toBe(researches);
    expect(researches).toContain('"title":null');

    await userEvent.click(screen.getByRole("button", { name: "Try it yourself" }));
    expect(await screen.findByText("Tell me what you look for at Slush 2026.")).toBeInTheDocument();
    expect(screen.queryByRole("heading", { level: 3 })).not.toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Message Grabbit" })).toHaveFocus();
    await waitFor(() =>
      expect(within(toasts).queryByText("Simulated event")).not.toBeInTheDocument(),
    );
    // The real app reads from the real API again.
    await waitFor(() => expect(calls.length).toBeGreaterThan(before));
  });

  it("advances when the visitor makes the move themselves", async () => {
    realApi();
    renderWithDemo();
    await userEvent.click(await screen.findByRole("button", { name: /See how it works/ }));
    await step(DEMO_STEPS[0].title);
    await userEvent.type(
      screen.getByRole("textbox", { name: "Message Grabbit" }),
      "Robotics at pre-seed{Enter}",
    );
    expect(await screen.findByText(DEMO_STEPS[0].outcome)).toBeInTheDocument();
  });

  it("leaves with Escape from the card, and with its close button", async () => {
    realApi();
    renderWithDemo();
    await userEvent.click(await screen.findByRole("button", { name: /See how it works/ }));
    await step(DEMO_STEPS[0].title);
    expect((await card()).getByText("Sample data, nothing is saved")).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 3 }).closest("section")).toHaveFocus();
    await userEvent.keyboard("{Escape}");
    expect(await screen.findByRole("button", { name: /See how it works/ })).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /See how it works/ }));
    await step(DEMO_STEPS[0].title);
    await userEvent.click(screen.getByRole("button", { name: "Exit the demo" }));
    expect(await screen.findByRole("button", { name: /See how it works/ })).toBeInTheDocument();
  });

  it("opens straight on the demo with ?tour, and drops the parameter on the way out", async () => {
    history.replaceState(null, "", "/?tour");
    realApi();
    renderWithDemo();
    await step(DEMO_STEPS[0].title);
    await userEvent.click(screen.getByRole("button", { name: "Exit the demo" }));
    await screen.findByRole("button", { name: /See how it works/ });
    expect(location.search).toBe("");
  });

  it("can be replayed from the sidebar foot at any time", async () => {
    realApi();
    renderWithDemo();
    const sidebar = await screen.findByRole("complementary");
    await userEvent.click(within(sidebar).getByRole("button", { name: "How Grabbit works" }));
    await step(DEMO_STEPS[0].title);
    expect(
      within(screen.getByRole("complementary")).queryByRole("button", {
        name: "How Grabbit works",
      }),
    ).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "New research" })).not.toBeInTheDocument();
  });

  it("puts the real API back when it unmounts mid-demo", async () => {
    const calls = realApi();
    const { unmount } = renderWithDemo();
    await userEvent.click(await screen.findByRole("button", { name: /See how it works/ }));
    await step(DEMO_STEPS[0].title);
    unmount();
    const before = calls.length;
    renderWithClient(<App />);
    expect(await screen.findByText("Tell me what you look for at Slush 2026.")).toBeInTheDocument();
    expect(calls.length).toBeGreaterThan(before);
  });

  it("shows no launcher where the app runs without the demo", async () => {
    realApi();
    renderWithClient(<App />);
    expect(await screen.findByText("Tell me what you look for at Slush 2026.")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /See how it works/ })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "How Grabbit works" })).not.toBeInTheDocument();
  });
});
