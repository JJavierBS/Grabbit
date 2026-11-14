import { candidates, reportV1 } from "../../dev/fixtures";
import { COL, layoutPath, NODE_W, toTall } from "./calaPath";

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

describe("hidden links on the path", () => {
  const northwind = candidates.find((c) => c.entity_id === "c-northwind");
  if (!northwind) throw new Error("fixture changed");
  const trusted = new Set(["i-aurora", "i-northstar"]);

  it("branches each link off its investor as a dashed, labelled line to a fifth column", () => {
    const { nodes, edges, width } = layoutPath(northwind, trusted, "Slush 2026");
    const links = nodes.filter((n) => n.kind === "link");
    expect(links.map((n) => [n.label, n.sub])).toEqual([
      ["Lumen Ledger", "on your list"],
      ["North Star Capital", "you trust"],
    ]);
    expect(links.every((n) => n.x === COL[4] && n.detail)).toBe(true);
    const dashed = edges.filter((e) => e.dashed);
    expect(dashed.map((e) => [e.from, e.label])).toEqual([
      ["i:0:i-aurora", "also backs"],
      ["i:0:i-fjordline", "co-invested 3×"],
    ]);
    expect(width).toBe(COL[4] + NODE_W);
    // No two nodes of one column overlap.
    const ys = (col: number) => nodes.filter((n) => n.x === col).map((n) => n.y);
    for (const col of COL) expect(new Set(ys(col)).size).toBe(ys(col).length);
  });

  it("puts an investor with a link ahead of other investors so its branch is drawn", () => {
    const round = northwind.rounds[0];
    const crowded = {
      ...northwind,
      rounds: [
        {
          ...round,
          investors: [inv("a", true), inv("b", true), inv("c", true), ...round.investors],
        },
      ],
    };
    const { nodes } = layoutPath(crowded, new Set(), "Slush 2026");
    const shown = nodes.filter((n) => n.kind === "investor").map((n) => n.entityId);
    expect(shown).toEqual(["i-aurora", "i-fjordline", "a"]);
  });

  it("keeps the width of the plain path when there is no link", () => {
    const { width } = layoutPath({ ...northwind, links: [] }, trusted, "Slush 2026");
    expect(width).toBe(COL[3] + NODE_W);
  });

  it("lists a link under its investor in the tall tree, with the claim in the sub line", () => {
    const tall = toTall(layoutPath(northwind, trusted, "Slush 2026"), 340);
    const at = tall.nodes.findIndex((n) => n.entityId === "i-fjordline");
    const link = tall.nodes[at + 1];
    expect(link.kind).toBe("link");
    expect(link.sub).toBe("co-invested 3× · you trust");
    expect(link.x).toBeGreaterThan(tall.nodes[at].x);
  });
});
