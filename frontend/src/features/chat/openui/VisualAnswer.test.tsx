import { Renderer } from "@openuidev/react-lang";
import { render, screen } from "@testing-library/react";
import { reportV1 } from "../../../dev/fixtures";
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

  it("says an id is not in the report instead of drawing it", () => {
    draw(`root = Answer([g])\ng = FactGrid("made-up-id", ["hq"])`);
    expect(screen.getByText(/Not in this report/)).toBeInTheDocument();
  });
});
