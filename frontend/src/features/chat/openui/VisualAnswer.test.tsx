import { Renderer } from "@openuidev/react-lang";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { exploredAnswerUi, exploredAurora, reportV1 } from "../../../dev/fixtures";
import { AnswerContext, answerLibrary } from "./library";

function draw(ui: string) {
  const c = reportV1.candidates[0];
  render(
    <AnswerContext.Provider value={{ candidates: new Map([[c.entity_id, c]]), trusted: new Set() }}>
      <Renderer response={ui} library={answerLibrary} />
    </AnswerContext.Provider>,
  );
  return c;
}

describe("visual answer", () => {
  it("draws the graph of a startup in the report from its Cala id", () => {
    const c = reportV1.candidates[0];
    draw(`root = Answer([g])\ng = CompanyGraph("${c.entity_id}")`);
    expect(screen.getByRole("heading", { name: `${c.name} in Cala's graph` })).toBeInTheDocument();
  });

  it("draws the walk in Cala and the sourced facts of an explored entity", async () => {
    render(
      <AnswerContext.Provider
        value={{
          candidates: new Map(),
          trusted: new Set(["i-northstar"]),
          explored: exploredAurora,
        }}
      >
        <Renderer response={exploredAnswerUi} library={answerLibrary} />
      </AnswerContext.Provider>,
    );
    expect(
      screen.getByRole("heading", { name: "Around Aurora Ventures in Cala's graph" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("img", { name: /walked in Cala's graph from Aurora/ }),
    ).toBeInTheDocument();
    expect(screen.getAllByText("raised")).toHaveLength(2);
    const trusted = screen.getByRole("button", { name: /North Star Capital/ });
    expect(trusted).toHaveAttribute("data-trusted", "true");
    // EntityFacts: the round's amount and date, each with a trust badge.
    expect(screen.getByText("€1.8M")).toBeInTheDocument();
    expect(screen.getByText("Mar 2025")).toBeInTheDocument();
    expect(screen.getAllByText(/Press|Official filing/).length).toBeGreaterThan(0);

    // Selecting a node shows its Cala id and facts under the drawing.
    await userEvent.click(screen.getByRole("button", { name: /Aurora Ventures/ }));
    expect(screen.getByText("i-aurora")).toBeInTheDocument();
    expect(screen.getByText("aurora.example")).toBeInTheDocument();
  });

  it("does not draw a walk the message does not carry", () => {
    draw('root = Answer([g])\ng = ExploredGraph("i-aurora")');
    expect(screen.getByText(/Not reached in Cala/)).toBeInTheDocument();
  });

  it("says an id is not in the report instead of drawing it", () => {
    draw(`root = Answer([g])\ng = FactGrid("made-up-id", ["hq"])`);
    expect(screen.getByText(/Not in this report/)).toBeInTheDocument();
  });
});
