import { reportV1 } from "../../dev/fixtures";
import { layoutPath, toTall } from "./calaPath";

const inv = (id: string, is_lead = false) => ({
  entity_id: id,
  name: id,
  is_lead,
  role: "investor" as const,
});

describe("layoutPath", () => {
  const base = reportV1.candidates[0];
  const candidate = {
    ...base,
    rounds: [
      {
        ...base.rounds[0],
        investors: [inv("a"), inv("b"), inv("lead", true), inv("trusted"), inv("c")],
      },
    ],
  };

  it("walks event, startup, round and investors with Cala's edge names", () => {
    const { edges } = layoutPath(candidate, new Set(), "Slush 2026");
    expect(edges.map((e) => e.label)).toEqual(
      expect.arrayContaining(["ATTENDEE", "ISSUER", "is_lead", "INVESTOR"]),
    );
  });

  it("shows investors you trust and the lead first, folds the rest", () => {
    const { nodes } = layoutPath(candidate, new Set(["trusted"]), "Slush 2026");
    const investors = nodes.filter((n) => n.kind === "investor");
    expect(investors.map((n) => n.label)).toEqual(["trusted", "lead", "a"]);
    expect(investors[0].sub).toBe("you trust");
    expect(nodes.find((n) => n.kind === "more")?.label).toBe("+2 more");
  });
});

describe("toTall", () => {
  it("puts each child under its parent with the relation in the sub line", () => {
    const c = reportV1.candidates[0];
    const tall = toTall(layoutPath(c, new Set(), "Slush 2026"), 320);
    const [event, startup, round, first] = tall.nodes;
    expect([event.kind, startup.kind, round.kind]).toEqual(["event", "startup", "round"]);
    expect(startup.sub).toBe("ATTENDEE");
    expect(round.sub).toMatch(/^ISSUER/);
    expect(first.x).toBeGreaterThan(round.x);
    expect(tall.nodes.every((n) => n.x + (n.w ?? 0) === 320)).toBe(true);
    expect(tall.nodes.map((n) => n.y)).toEqual(tall.nodes.map((_, i) => i * 46));
  });
});
