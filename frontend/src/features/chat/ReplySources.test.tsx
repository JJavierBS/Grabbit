import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ChatMessage, ReplySource } from "../../api/types";
import { mockApi, renderWithClient } from "../../test/renderApp";
import { ChatPanel } from "./ChatPanel";
import { ReplySources, summaryText } from "./ReplySources";

const src = (
  name: string,
  rank: ReplySource["sources"][number]["rank"],
  url: string | null = null,
) => ({
  name,
  rank,
  url,
  date: null,
  date_precision: null,
});

const cited: ReplySource[] = [
  {
    entity_id: "c-grei",
    name: "GREÏ",
    sources: [
      src("eu-startups.com", "press", "https://eu-startups.com/a"),
      src("linkedin.com", "aggregator"),
    ],
  },
  {
    entity_id: "c-eka",
    name: "Eka Labs AI",
    sources: [
      src("find-and-update.company-information.service.gov.uk", "filing", "https://x.gov.uk"),
      src("linkedin.com", "aggregator"),
      src("eka.ai", "primary"),
    ],
  },
];

describe("Sources under a reply", () => {
  it("sums every source up once, strongest first", () => {
    expect(summaryText(cited)).toBe(
      "find-and-update.company-information.service.gov.uk, eka.ai, eu-startups.com and 1 more",
    );
    expect(summaryText([cited[0]])).toBe("eu-startups.com, linkedin.com");
  });

  it("opens to each startup's sources with a written trust label and a link", async () => {
    render(<ReplySources cited={cited} />);
    const grei = screen.getByRole("list", { name: "Sources for GREÏ" });
    expect(grei).not.toBeVisible();
    await userEvent.click(screen.getByText("Sources"));
    expect(grei).toBeVisible();
    // The trust level is written out, not an icon alone.
    expect(within(grei).getByText("Press")).toBeVisible();
    expect(within(grei).getByRole("link", { name: "eu-startups.com" })).toHaveAttribute(
      "href",
      "https://eu-startups.com/a",
    );
    expect(within(grei).queryByRole("link", { name: "linkedin.com" })).toBeNull();
    expect(within(grei).getByText("linkedin.com")).toBeVisible();
  });

  it("shows only under prose replies that cite startups", async () => {
    const message = (id: string, over: Partial<ChatMessage>): ChatMessage => ({
      id,
      role: "agent",
      text: "GREÏ raised a pre-seed.",
      created_at: "2026-11-14T09:00:00Z",
      profile_changes: [],
      report_id: null,
      ui: null,
      graph: null,
      walk: null,
      sources: [],
      ...over,
    });
    mockApi({
      "GET /api/chat": () => [
        message("a1", { sources: cited }),
        message("a2", { text: "Noted." }),
        message("a3", { ui: 'root = Answer([t])\nt = Text("GREÏ.")', sources: cited }),
      ],
    });
    renderWithClient(<ChatPanel />);
    expect(await screen.findAllByText("Sources")).toHaveLength(1);
  });
});
