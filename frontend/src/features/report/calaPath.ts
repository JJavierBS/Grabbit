import type { Candidate, Round } from "../../api/types";

/** One node of the path drawn under a candidate: each one is a Cala entity. */
export interface PathNode {
  id: string;
  kind: "event" | "startup" | "round" | "investor" | "more";
  label: string;
  sub?: string;
  /** Cala entity id, for the detail line. */
  entityId?: string;
  lead?: boolean;
  trusted?: boolean;
  x: number;
  y: number;
  /** Width in the tall layout; the wide one uses NODE_W. */
  w?: number;
}

export interface PathEdge {
  from: string;
  to: string;
  /** The Cala edge it stands for, as the graph names it. */
  label: string;
  strong?: boolean;
}

export interface PathLayout {
  nodes: PathNode[];
  edges: PathEdge[];
  width: number;
  height: number;
  tall?: boolean;
}

export const NODE_W = 128;
export const COL = [0, 192, 384, 576];
export const ROW = 46;
const MAX_ROUNDS = 2;
const MAX_INVESTORS = 3;

function roundTitle(r: Round): string {
  const label = r.label ?? r.name;
  return label
    .replace(/_/g, " ")
    .toLowerCase()
    .replace(/^\w/, (c) => c.toUpperCase());
}

function newestFirst(rounds: Round[]): Round[] {
  return [...rounds].sort((a, b) =>
    String(b.date.value ?? "").localeCompare(String(a.date.value ?? "")),
  );
}

/**
 * The walk Grabbit did in Cala's graph to put this startup on the list:
 * event -> attendee -> its rounds as issuer -> who led or joined; investors you trust glow.
 * Investors you trust and leads come first; the rest fold into "+N more".
 */
export function layoutPath(c: Candidate, trusted: Set<string>, eventName: string): PathLayout {
  const nodes: PathNode[] = [];
  const edges: PathEdge[] = [];
  const rounds = newestFirst(c.rounds).slice(0, MAX_ROUNDS);
  const followOn = c.signals.find((s) => s.kind === "lead_follow_on");
  const followText =
    typeof followOn?.value === "number"
      ? `follows on ${Math.round(followOn.value * 100)}%`
      : undefined;

  let row = 0;
  const roundRows: number[] = [];
  rounds.forEach((r, ri) => {
    const rank = (i: Round["investors"][number]) =>
      (trusted.has(i.entity_id) ? 0 : 2) + (i.is_lead ? 0 : 1);
    const sorted = [...r.investors].sort((a, b) => rank(a) - rank(b));
    const shown = sorted.slice(0, MAX_INVESTORS);
    const hidden = sorted.length - shown.length;
    const first = row;
    const roundId = `r:${r.entity_id}`;
    shown.forEach((inv) => {
      const id = `i:${ri}:${inv.entity_id}`;
      const isTrusted = trusted.has(inv.entity_id);
      nodes.push({
        id,
        kind: "investor",
        label: inv.name,
        sub:
          [
            isTrusted && "you trust",
            inv.is_lead && "lead",
            !isTrusted && inv.is_lead && ri === 0 && followText,
          ]
            .filter(Boolean)
            .join(" · ") || undefined,
        entityId: inv.entity_id,
        lead: inv.is_lead,
        trusted: isTrusted,
        x: COL[3],
        y: row * ROW,
      });
      edges.push({
        from: roundId,
        to: id,
        label: inv.is_lead ? "is_lead" : inv.role.toUpperCase(),
        strong: isTrusted,
      });
      row += 1;
    });
    if (hidden > 0) {
      nodes.push({
        id: `m:${ri}`,
        kind: "more",
        label: `+${hidden} more`,
        x: COL[3],
        y: row * ROW,
      });
      edges.push({ from: roundId, to: `m:${ri}`, label: "" });
      row += 1;
    }
    if (shown.length === 0) {
      nodes.push({
        id: `m:${ri}`,
        kind: "more",
        label: "No investor published",
        x: COL[3],
        y: row * ROW,
      });
      edges.push({ from: roundId, to: `m:${ri}`, label: "" });
      row += 1;
    }
    const y = ((first + row - 1) / 2) * ROW;
    roundRows.push(y);
    const when = typeof r.date.value === "string" ? r.date.value.slice(0, 7) : undefined;
    nodes.push({
      id: roundId,
      kind: "round",
      label: roundTitle(r),
      sub: when,
      entityId: r.entity_id,
      x: COL[2],
      y,
    });
    edges.push({
      from: `s:${c.entity_id}`,
      to: roundId,
      label: "ISSUER",
      strong: r.investors.some((i) => trusted.has(i.entity_id)),
    });
  });

  const height = Math.max(row, 1) * ROW;
  const mid = roundRows.length ? roundRows.reduce((a, b) => a + b, 0) / roundRows.length : 0;
  nodes.push({
    id: `s:${c.entity_id}`,
    kind: "startup",
    label: c.name,
    entityId: c.entity_id,
    x: COL[1],
    y: mid,
  });
  nodes.push({ id: "event", kind: "event", label: eventName, x: COL[0], y: mid });
  edges.push({ from: "event", to: `s:${c.entity_id}`, label: "ATTENDEE" });

  return { nodes, edges, width: COL[3] + NODE_W, height };
}

const INDENT = 22;

/**
 * The same path as an indented tree, for narrow columns (chat, side panel): one node per
 * row, children under their parent. The relation moves into the sub line.
 */
export function toTall(wide: PathLayout, width: number): PathLayout {
  const kids = new Map<string, PathEdge[]>();
  for (const e of wide.edges) kids.set(e.from, [...(kids.get(e.from) ?? []), e]);
  const byId = new Map(wide.nodes.map((n) => [n.id, n]));
  const nodes: PathNode[] = [];
  const visit = (id: string, depth: number, via?: PathEdge) => {
    const n = byId.get(id);
    if (!n) return;
    const x = depth * INDENT;
    const relation = via && ["ATTENDEE", "ISSUER"].includes(via.label) ? via.label : undefined;
    const sub = [relation, n.sub].filter(Boolean).join(" · ") || undefined;
    nodes.push({ ...n, sub, x, y: nodes.length * ROW, w: width - x });
    for (const e of kids.get(id) ?? []) visit(e.to, depth + 1, e);
  };
  visit("event", 0);
  return { nodes, edges: wide.edges, width, height: nodes.length * ROW, tall: true };
}
