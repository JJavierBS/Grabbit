import { render, screen, within } from "@testing-library/react";
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

  it("shows readable stages, sectors and round names, never Cala's enums", () => {
    const base = reportV1.candidates[0];
    const candidate = {
      ...base,
      industries: ["SOFTWARE_AND_SERVICES", "ai", "AI"],
      funding_stage: { ...base.funding_stage, value: "PRE_SEED" },
      rounds: base.rounds.slice(0, 1).map((r) => ({ ...r, label: "SERIES_A" })),
    };
    const { container } = render(<CandidateCard candidate={candidate} trusted={new Set()} />);
    const tags = screen.getByRole("list", { name: "Industries" });
    expect(tags).toHaveTextContent("Software and services");
    expect(tags).toHaveTextContent("AI");
    expect(within(tags).getAllByRole("listitem")).toHaveLength(2);
    expect(container).toHaveTextContent("Pre-seed");
    expect(container).toHaveTextContent("Series A");
    expect(container.textContent).not.toMatch(/PRE_SEED|SOFTWARE_AND_SERVICES|SERIES_A/);
  });
});
