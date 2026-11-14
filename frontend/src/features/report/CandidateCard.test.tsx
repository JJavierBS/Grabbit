import { render, screen } from "@testing-library/react";
import { reportV1 } from "../../dev/fixtures";
import { CandidateCard } from "./CandidateCard";

describe("CandidateCard", () => {
  it("separates several leads of one round", () => {
    const base = reportV1.candidates[0];
    const [round] = base.rounds;
    const candidate = {
      ...base,
      rounds: [
        {
          ...round,
          investors: [
            { entity_id: "i-yc", name: "Y Combinator", is_lead: true, role: "investor" as const },
            {
              entity_id: "i-630",
              name: "SixThirty Cyber Fund",
              is_lead: true,
              role: "investor" as const,
            },
          ],
        },
      ],
    };
    render(<CandidateCard candidate={candidate} trusted={new Set()} />);
    expect(screen.getByText(/Led by/).parentElement).toHaveTextContent(
      "Led by Y Combinator, SixThirty Cyber Fund",
    );
  });
});
