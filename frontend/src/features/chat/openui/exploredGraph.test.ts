import type { ExploredGraph } from "../../../api/types";
import { exploredAurora } from "../../../dev/fixtures";
import { layoutWalk, MAX_CHILDREN, NODE_W, PITCH, toTallWalk } from "./exploredGraph";

const trusted = new Set(["i-northstar"]);

describe("layoutWalk", () => {
  const layout = layoutWalk(exploredAurora, "i-aurora", trusted);
  const node = (id: string) => layout.nodes.find((n) => n.id === id);

  it("puts the root on the left and each hop one column to the right", () => {
    expect(node("i-aurora")).toMatchObject({ kind: "root", depth: 0, x: 0 });
    expect(node("r-fjord-seed")).toMatchObject({ kind: "round", depth: 1, x: PITCH });
    expect(node("c-fjord")).toMatchObject({ depth: 2, x: 2 * PITCH });
    expect(layout.width).toBe(2 * PITCH + NODE_W);
  });

  it("labels lines with readable edge names and roles", () => {
    const label = (from: string, to: string) =>
      layout.edges.find((e) => e.from === from && e.to === to)?.label;
    expect(label("i-aurora", "r-fjord-seed")).toBe("led");
    expect(label("r-fjord-seed", "c-fjord")).toBe("raised");
    expect(label("i-aurora", "p-lina")).toBe("founded");
  });

  it("highlights investors you trust, the way to them, and leads", () => {
    expect(node("i-northstar")).toMatchObject({ trusted: true });
    expect(node("i-northstar")?.sub).toMatch(/^you trust/);
    expect(node("i-birch")).toMatchObject({ lead: true });
    const strong = layout.edges.filter((e) => e.strong && !e.cross).map((e) => e.to);
    expect(strong).toEqual(expect.arrayContaining(["r-fjord-seed", "i-northstar"]));
  });

  it("draws each entity once and keeps a second link as a cross edge", () => {
    expect(layout.nodes.filter((n) => n.id === "i-northstar")).toHaveLength(1);
    expect(layout.edges.filter((e) => e.cross)).toHaveLength(1);
  });

  it("starts from the first node when the root id is unknown", () => {
    expect(
      layoutWalk(exploredAurora, "nope", trusted).nodes.find((n) => n.kind === "root")?.id,
    ).toBe("i-aurora");
  });

  it("folds a long list into +N more", () => {
    const many: ExploredGraph = {
      nodes: [
        { entity_id: "root", name: "Root", entity_type: "Company", facts: {} },
        ...Array.from({ length: MAX_CHILDREN + 3 }, (_, i) => ({
          entity_id: `n${i}`,
          name: `N${i}`,
          entity_type: "Company",
          facts: {},
        })),
      ],
      edges: Array.from({ length: MAX_CHILDREN + 3 }, (_, i) => ({
        source: `n${i}`,
        target: "root",
        relationship: "INVESTED_IN",
        role: null,
        is_lead: false,
        facts: {},
      })),
    };
    const { nodes } = layoutWalk(many, "root", new Set());
    expect(nodes.filter((n) => n.depth === 1 && n.kind !== "more")).toHaveLength(MAX_CHILDREN);
    expect(nodes.find((n) => n.kind === "more")?.label).toBe("+3 more");
  });
});

describe("toTallWalk", () => {
  it("lists one node per row, children indented under their parent, no cross edges", () => {
    const tall = toTallWalk(layoutWalk(exploredAurora, "i-aurora", trusted), 320);
    expect(tall.tall).toBe(true);
    expect(tall.nodes[0].id).toBe("i-aurora");
    expect(new Set(tall.nodes.map((n) => n.y)).size).toBe(tall.nodes.length);
    const round = tall.nodes.find((n) => n.id === "r-fjord-seed");
    const issuer = tall.nodes.find((n) => n.id === "c-fjord");
    expect(issuer?.x).toBeGreaterThan(round?.x ?? 0);
    expect(issuer?.sub).toMatch(/^raised/);
    expect(tall.edges.some((e) => e.cross)).toBe(false);
    expect(Math.max(...tall.nodes.map((n) => n.x + (n.w ?? 0)))).toBeLessThanOrEqual(320);
  });

  it("does not repeat the edge's word in a node's sub line", () => {
    const tall = toTallWalk(layoutWalk(exploredAurora, "i-aurora", trusted), 320);
    for (const n of tall.nodes) {
      const parts = (n.sub ?? "").toLowerCase().split(" · ");
      if (parts[0] === "led") expect(parts).not.toContain("lead investor");
      if (parts[0] === "invested") expect(parts).not.toContain("investor");
      expect(n.sub ?? "").not.toMatch(/is_lead|[A-Z]{3,}_/);
    }
  });
});
