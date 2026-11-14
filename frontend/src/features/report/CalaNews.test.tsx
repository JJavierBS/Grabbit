import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { reportV1 } from "../../dev/fixtures";
import { CalaNews } from "./CalaNews";
import { CandidateCard } from "./CandidateCard";

const northwind = reportV1.candidates[0];

describe("CalaNews", () => {
  it("labels the block as Cala news, never as a web signal", () => {
    render(<CalaNews items={northwind.news} name={northwind.name} />);
    const block = screen.getByRole("region", { name: `News about ${northwind.name} from Cala` });
    expect(within(block).getByText("Cala news").closest("[data-trust]")).toHaveAttribute(
      "data-trust",
      "cala_news",
    );
    expect(within(block).queryByText("Web, unverified")).not.toBeInTheDocument();
    // Cala gives no per-item source, so nothing in the block is a link.
    expect(within(block).queryByRole("link")).not.toBeInTheDocument();
  });

  it("shows each date only at its precision", () => {
    const lumen = reportV1.candidates[1];
    render(<CalaNews items={[...northwind.news, ...lumen.news]} name="Mixed" />);
    expect(screen.getByText("3 Nov 2026")).toHaveAttribute("dateTime", "2026-11-03");
    expect(screen.getByText("Oct 2026")).toBeInTheDocument();
    expect(screen.getByText("Date not published")).toBeInTheDocument();
  });

  it("shows mentioned entities as chips carrying their Cala ids", () => {
    render(<CalaNews items={northwind.news} name={northwind.name} />);
    const chips = within(screen.getByRole("list", { name: "Mentioned in Cala" })).getAllByRole(
      "listitem",
    );
    expect(chips.map((c) => c.getAttribute("data-entity-id"))).toEqual([
      "e-baltic-ferries",
      "e-tallinn",
    ]);
    expect(chips[0]).toHaveAttribute("title", "Company in Cala, id e-baltic-ferries");
  });

  it("folds a long summary to one line and expands it on request", async () => {
    render(<CalaNews items={northwind.news} name={northwind.name} />);
    const more = screen.getByRole("button", { name: "More" });
    const summary = screen.getByText(/measure fuel use/);
    expect(summary).toHaveAttribute("data-open", "false");
    await userEvent.click(more);
    expect(summary).toHaveAttribute("data-open", "true");
    expect(more).toHaveAttribute("aria-expanded", "true");
    expect(more).toHaveTextContent("Less");
  });

  it("draws nothing without news", () => {
    const { container } = render(<CalaNews items={[]} name="Quiet Oy" />);
    expect(container).toBeEmptyDOMElement();
  });

  it("appears on the candidate card", () => {
    render(<CandidateCard candidate={northwind} trusted={new Set()} />);
    expect(
      screen.getByRole("region", { name: `News about ${northwind.name} from Cala` }),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Northwind Labs opens a pilot with a Baltic ferry operator"),
    ).toBeVisible();
  });
});
