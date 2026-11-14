import { Renderer } from "@openuidev/react-lang";
import { render, screen } from "@testing-library/react";
import type { Candidate } from "../../../api/types";
import { reportV1 } from "../../../dev/fixtures";
import { AnswerContext, answerLibrary } from "./library";

function draw(ui: string, candidates: Candidate[]) {
  render(
    <AnswerContext.Provider
      value={{ candidates: new Map(candidates.map((c) => [c.entity_id, c])), trusted: new Set() }}
    >
      <Renderer response={ui} library={answerLibrary} />
    </AnswerContext.Provider>,
  );
}

describe("News in a chat answer", () => {
  it("draws a startup's Cala news from the report by its id", () => {
    const c = reportV1.candidates[0];
    draw(`root = Answer([n])\nn = News("${c.entity_id}")`, [c]);
    expect(screen.getByRole("region", { name: `News about ${c.name} from Cala` })).toBeVisible();
    expect(screen.getByText(c.news[0].title)).toBeInTheDocument();
  });

  it("says when Cala has no news instead of drawing an empty block", () => {
    const quiet = reportV1.candidates[2];
    draw(`root = Answer([n])\nn = News("${quiet.entity_id}")`, [quiet]);
    expect(screen.getByText(`No news about ${quiet.name} in Cala yet.`)).toBeInTheDocument();
  });

  it("refuses an id that is not in the report", () => {
    draw(`root = Answer([n])\nn = News("made-up-id")`, []);
    expect(screen.getByText(/Not in this report/)).toBeInTheDocument();
  });
});
