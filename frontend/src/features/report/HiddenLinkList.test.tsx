import { Renderer } from "@openuidev/react-lang";
import { render, screen, within } from "@testing-library/react";
import { candidates } from "../../dev/fixtures";
import { AnswerContext, answerLibrary } from "../chat/openui/library";
import { CandidateCard } from "./CandidateCard";

const northwind = candidates[0];
const saltmarsh = candidates[3];

describe("hidden links", () => {
  it("lists each link on the card with its investor, proof rounds and trust", () => {
    render(<CandidateCard candidate={northwind} trusted={new Set(["i-northstar"])} />);
    const section = screen.getByRole("region", { name: "Hidden links of Northwind Labs" });
    const item = within(section)
      .getByText("Fjordline Angels co-invested 3× with North Star Capital")
      .closest("li");
    if (!item) throw new Error("no list item");
    expect(item).toHaveTextContent("Pinecone Grid · Seed");
    expect(within(item).getAllByText("Press").length).toBeGreaterThan(0);
  });

  it("hides the section when Cala shows no link", () => {
    render(<CandidateCard candidate={saltmarsh} trusted={new Set()} />);
    expect(screen.queryByRole("region", { name: /Hidden links/ })).toBeNull();
  });

  it("draws them in a chat answer from the startup's Cala id", () => {
    render(
      <AnswerContext.Provider
        value={{ candidates: new Map(candidates.map((c) => [c.entity_id, c])), trusted: new Set() }}
      >
        <Renderer
          response={`root = Answer([a, b])\na = HiddenLinks("c-northwind")\nb = HiddenLinks("c-saltmarsh")`}
          library={answerLibrary}
        />
      </AnswerContext.Provider>,
    );
    expect(screen.getByText("Aurora Ventures also backs Lumen Ledger")).toBeInTheDocument();
    expect(screen.getByText("No hidden link found in Cala's graph.")).toBeInTheDocument();
  });
});
